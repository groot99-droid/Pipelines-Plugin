class PublishError(Exception):
    """Base class; the CLI prints the message and exits non-zero."""


class ValidationFailed(PublishError):
    def __init__(self, platform: str, issues: list):
        self.platform, self.issues = platform, issues
        super().__init__(f"{platform}: " + "; ".join(i.message for i in issues))


class AuthError(PublishError):
    """Missing, expired or revoked credentials."""


class NotAllowed(PublishError):
    """A safety rule refused the request (no confirmation, public without opt-in, duplicate send, ...)."""


class ApiError(PublishError):
    def __init__(self, platform: str, status: int, message: str):
        self.platform, self.status = platform, status
        super().__init__(f"{platform} API error {status}: {message}")
