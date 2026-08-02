class FRMError(Exception):
    """Base exception for all FRM client errors."""


class FRMConnectionError(FRMError):
    """Raised when the FRM web server could not be reached."""


class FRMAuthenticationError(FRMError):
    """Raised when a request is rejected due to a missing or invalid FRM token."""


class FRMRequestError(FRMError):
    """Raised when the FRM server returns an error response."""
