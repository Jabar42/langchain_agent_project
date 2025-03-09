import pytest
from unittest.mock import Mock, patch
from src.models.model_manager import ModelManager
from src.utils.exceptions import ModelNotFoundError, ModelConfigError

@pytest.fixture
def model_manager():
    """Create a ModelManager instance for testing."""
    with patch('src.models.model_manager.ChatOpenAI'), \
         patch('src.models.model_manager.ChatAnthropic'), \
         patch('src.models.model_manager.ChatCohere'), \
         patch('src.models.model_manager.genai'):
        return ModelManager()

def test_register_model(model_manager):
    """Test registering a new model."""
    mock_model = Mock()
    model_manager.register_model("test-model", mock_model)
    assert "test-model" in model_manager.models
    assert model_manager.models["test-model"] == mock_model

def test_get_model_success(model_manager):
    """Test getting an existing model."""
    mock_model = Mock()
    model_manager.register_model("test-model", mock_model)
    retrieved_model = model_manager.get_model("test-model")
    assert retrieved_model == mock_model

def test_get_model_not_found(model_manager):
    """Test getting a non-existent model raises error."""
    with pytest.raises(ModelNotFoundError):
        model_manager.get_model("non-existent-model")

def test_get_default_models(model_manager):
    """Test getting default model list."""
    default_models = model_manager.get_default_models()
    assert isinstance(default_models, list)
    assert len(default_models) > 0
    assert "gpt-4" in default_models

def test_list_available_models(model_manager):
    """Test listing available models."""
    mock_model = Mock()
    model_manager.register_model("test-model", mock_model)
    available_models = model_manager.list_available_models()
    assert "test-model" in available_models

def test_remove_model(model_manager):
    """Test removing a model."""
    mock_model = Mock()
    model_manager.register_model("test-model", mock_model)
    model_manager.remove_model("test-model")
    assert "test-model" not in model_manager.models

def test_get_best_available_model(model_manager):
    """Test getting best available model."""
    mock_model = Mock()
    model_manager.register_model("gpt-4", mock_model)
    best_model = model_manager.get_best_available_model()
    assert best_model == "gpt-4"

@patch('os.getenv')
def test_google_api_key_not_found(mock_getenv, model_manager):
    """Test error when Google API key is not found."""
    mock_getenv.return_value = None
    with pytest.raises(ModelConfigError):
        model_manager._get_google_api_key()

@patch('os.getenv')
def test_google_api_key_found(mock_getenv, model_manager):
    """Test successful retrieval of Google API key."""
    mock_getenv.return_value = "test-api-key"
    api_key = model_manager._get_google_api_key()
    assert api_key == "test-api-key" 