"""`ve publish`: send a finished video to social platforms through their OFFICIAL APIs only.

Design rules (enforced in service.py and covered by tests, not just documented):
  * OAuth or app tokens only. No passwords, no cookies, no headless browser login, no user-agent spoofing.
  * Secrets live in the OS keyring (or environment variables). Never in a file this tool writes.
  * Dry-run is the default. Sending needs an explicit confirmation per platform.
  * Private/draft is the default wherever a platform offers it; public posting needs an explicit `public` opt-in.
  * An idempotency ledger stops a retry from posting twice.
"""
