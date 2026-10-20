class REBError(Exception):
    """User-facing, controlled REB error."""

class PermissionRequired(REBError):
    """A potentially consequential action needs approval."""

class MissingProvider(REBError):
    """Optional external integration has not been configured."""
