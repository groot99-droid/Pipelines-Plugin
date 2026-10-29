"""OAuth 2.0 authorization-code flow with PKCE for a locally run app (loopback redirect), plus token refresh.

Only stdlib + requests. The loopback listener binds 127.0.0.1 only, accepts exactly one callback, checks the
`state` parameter and times out. Tokens are stored through secrets.py (keyring/env), never in a file.
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import json
import secrets as pysecrets
import time
import urllib.parse
from dataclasses import asdict, dataclass, field

from videoeditor.publish import net as vhttp
from videoeditor.publish import secrets
from videoeditor.publish.errors import AuthError


@dataclass
class OAuthConfig:
    platform: str
    auth_url: str
    token_url: str
    client_id: str
    scopes: list[str]
    client_secret: str | None = None
    client_id_param: str = "client_id"              # TikTok calls it client_key
    scope_sep: str = " "
    extra_auth_params: dict = field(default_factory=dict)
    pkce: bool = True
    token_auth: str = "body"                        # "body" or "basic" (client credentials location)


@dataclass
class TokenSet:
    access_token: str
    refresh_token: str | None = None
    expires_at: float | None = None
    scope: str | None = None
    extra: dict = field(default_factory=dict)

    def expired(self, skew: float = 60) -> bool:
        return self.expires_at is not None and time.time() >= self.expires_at - skew


def pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(pysecrets.token_bytes(48)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def build_auth_url(cfg: OAuthConfig, redirect_uri: str, state: str, challenge: str | None) -> str:
    q = {cfg.client_id_param: cfg.client_id, "redirect_uri": redirect_uri, "response_type": "code",
         "scope": cfg.scope_sep.join(cfg.scopes), "state": state, **cfg.extra_auth_params}
    if cfg.pkce and challenge:
        q.update(code_challenge=challenge, code_challenge_method="S256")
    return cfg.auth_url + ("&" if "?" in cfg.auth_url else "?") + urllib.parse.urlencode(q)


def _token_request(cfg: OAuthConfig, data: dict) -> TokenSet:
    kw: dict = {}
    data = dict(data)
    if cfg.token_auth == "basic" and cfg.client_secret:
        kw["auth"] = (cfg.client_id, cfg.client_secret)
    else:
        data[cfg.client_id_param] = cfg.client_id
        if cfg.client_secret:
            data["client_secret"] = cfg.client_secret
    resp = vhttp.request(cfg.platform, "POST", cfg.token_url, data=data, ok=(200,), retries=1, **kw)
    body = resp.json()
    if "access_token" not in body:
        raise AuthError(f"{cfg.platform}: token endpoint returned no access_token")
    expires = body.get("expires_in")
    return TokenSet(access_token=body["access_token"], refresh_token=body.get("refresh_token"),
                    expires_at=time.time() + float(expires) if expires else None, scope=body.get("scope"),
                    extra={k: v for k, v in body.items() if k not in ("access_token", "refresh_token", "expires_in", "scope")})


def exchange_code(cfg: OAuthConfig, code: str, redirect_uri: str, verifier: str | None) -> TokenSet:
    data = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri}
    if cfg.pkce and verifier:
        data["code_verifier"] = verifier
    return _token_request(cfg, data)


def refresh(cfg: OAuthConfig, token: TokenSet) -> TokenSet:
    if not token.refresh_token:
        raise AuthError(f"{cfg.platform}: access token expired and there is no refresh token; run `ve publish init {cfg.platform}` again")
    new = _token_request(cfg, {"grant_type": "refresh_token", "refresh_token": token.refresh_token})
    if not new.refresh_token:       # many providers only return a refresh token when it rotates
        new.refresh_token = token.refresh_token
    return new


class _Handler(http.server.BaseHTTPRequestHandler):
    result: dict = {}

    def do_GET(self):  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        q = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}
        if parsed.path == "/callback" and ("code" in q or "error" in q):
            type(self).result = q
            body, status = b"Authorization received. You can close this tab and return to the terminal.", 200
        else:                      # favicon requests, port scanners, anything that is not the redirect
            body, status = b"not found", 404
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # keep codes and tokens out of logs
        pass


def loopback_authorize(cfg: OAuthConfig, *, port: int = 0, timeout: float = 300, say=print) -> TokenSet:
    """Run the whole flow. Prints the URL for the user to open (works headless: open it on any machine that can
    reach 127.0.0.1:<port>, e.g. via SSH port forwarding)."""
    state = pysecrets.token_urlsafe(24)
    verifier, challenge = pkce_pair() if cfg.pkce else (None, None)
    _Handler.result = {}
    server = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    redirect_uri = f"http://127.0.0.1:{server.server_address[1]}/callback"
    url = build_auth_url(cfg, redirect_uri, state, challenge)
    say(f"Open this URL in a browser and approve access:\n\n{url}\n\nWaiting for the redirect to {redirect_uri} ...")
    deadline = time.monotonic() + timeout
    server.timeout = 1.0
    try:
        while not _Handler.result and time.monotonic() < deadline:
            server.handle_request()
    finally:
        server.server_close()
    res = _Handler.result
    if not res:
        raise AuthError("timed out waiting for the authorization redirect")
    if res.get("state") != state:
        raise AuthError("state mismatch on the OAuth redirect; aborting")
    if "error" in res or "code" not in res:
        raise AuthError(f"authorization failed: {res.get('error_description') or res.get('error') or 'no code returned'}")
    return exchange_code(cfg, res["code"], redirect_uri, verifier)


# -------- storage + automatic refresh ---------------------------------------


def save_token(platform: str, token: TokenSet) -> None:
    secrets.set_json(platform, "token", asdict(token))


def load_token(platform: str) -> TokenSet | None:
    raw = secrets.get_json(platform, "token")
    return TokenSet(**raw) if raw else None


def access_token(cfg: OAuthConfig) -> str:
    """A valid access token for the platform, refreshed (and re-saved) when it is about to expire."""
    tok = load_token(cfg.platform)
    if tok is None:
        raise AuthError(f"{cfg.platform}: not logged in. Run `ve publish init {cfg.platform}`.")
    if tok.expired():
        tok = refresh(cfg, tok)
        try:
            save_token(cfg.platform, tok)
        except RuntimeError:
            pass    # env-var credentials cannot be updated; the refreshed token is used for this run only
    return tok.access_token


def json_dumps_token(token: TokenSet) -> str:
    return json.dumps(asdict(token))


def manual_authorize(cfg: OAuthConfig, redirect_uri: str, *, ask=input, say=print) -> TokenSet:
    """For providers that insist on a registered (often HTTPS) redirect URI that this tool cannot listen on.
    The user approves in a browser, lands on the redirect URL (the page may fail to load; that is fine) and
    pastes that URL, or just the code, back here."""
    state = pysecrets.token_urlsafe(24)
    verifier, challenge = pkce_pair() if cfg.pkce else (None, None)
    say(f"Open this URL, approve access, then copy the address of the page you land on:\n\n"
        f"{build_auth_url(cfg, redirect_uri, state, challenge)}\n")
    pasted = ask("Paste the full redirected URL (or only the code): ").strip()
    if "://" in pasted or pasted.startswith("?") or "code=" in pasted:
        q = {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query).items()}
        if "state" in q and q["state"] != state:
            raise AuthError("state mismatch in the pasted URL; aborting")
        if "error" in q:
            raise AuthError(f"authorization failed: {q.get('error_description') or q['error']}")
        code = q.get("code")
    else:
        code = pasted
    if not code:
        raise AuthError("no authorization code found in what you pasted")
    return exchange_code(cfg, code, redirect_uri, verifier)


def run_init(platform: str, build_cfg, *, ask=input, ask_secret=None, say=print, manual: bool = False,
             port: int = 0, redirect_uri: str | None = None, needs_secret: bool = False) -> str:
    """Shared `ve publish init` for OAuth platforms: client id/secret, browser authorization, token storage."""
    import getpass

    ask_secret = ask_secret or getpass.getpass
    client_id = secrets.get(platform, "client_id") or ask(f"{platform} client id: ").strip()
    client_secret = secrets.get(platform, "client_secret")
    if not client_secret:
        client_secret = ask_secret(f"{platform} client secret ({'required' if needs_secret else 'Enter to skip'}, hidden): ").strip() or None
    if needs_secret and not client_secret:
        raise AuthError(f"{platform} needs a client secret")
    cfg = build_cfg(client_id, client_secret)
    keyring_ok = secrets.keyring_available()
    token = (manual_authorize(cfg, redirect_uri, ask=ask, say=say) if manual
             else loopback_authorize(cfg, port=port, say=say))
    if keyring_ok:
        secrets.set(platform, "client_id", client_id)
        if client_secret:
            secrets.set(platform, "client_secret", client_secret)
        save_token(platform, token)
        return f"{platform}: logged in; token stored in the OS keyring"
    say("No OS keyring is available, so nothing was saved (this tool never writes secrets to files).")
    if ask("Print the token JSON once so you can export it as an environment variable? [y/N] ").strip().lower() == "y":
        say(f"export {secrets.env_name(platform, 'token')}='{json_dumps_token(token)}'\n"
            f"export {secrets.env_name(platform, 'client_id')}='{client_id}'"
            + (f"\nexport {secrets.env_name(platform, 'client_secret')}='<your secret>'" if client_secret else ""))
    return f"{platform}: authorized, not stored"
