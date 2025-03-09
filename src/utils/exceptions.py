class BaseAgentError(Exception):
    """Base exception class for all agent-related errors."""
    pass

class ModelError(BaseAgentError):
    """Base exception class for model-related errors."""
    pass

class ModelNotFoundError(ModelError):
    """Raised when a requested model is not found."""
    pass

class ModelConfigError(ModelError):
    """Raised when there's an error in model configuration."""
    pass

class EvaluationError(BaseAgentError):
    """Raised when there's an error in response evaluation."""
    pass

class ConnectorError(BaseAgentError):
    """Base exception class for connector-related errors."""
    pass

class TelegramError(ConnectorError):
    """Raised when there's an error in Telegram operations."""
    pass

class ThreadsError(ConnectorError):
    """Raised when there's an error in Threads operations."""
    pass

class ValidationError(BaseAgentError):
    """Raised when input validation fails."""
    pass

class RateLimitError(BaseAgentError):
    """Raised when rate limits are exceeded."""
    pass

class AuthenticationError(BaseAgentError):
    """Raised when authentication fails."""
    pass

class ConfigurationError(BaseAgentError):
    """Raised when there's an error in configuration."""
    pass 