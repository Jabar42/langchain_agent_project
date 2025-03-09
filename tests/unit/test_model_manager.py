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

@patch('os.getenv')
def test_anthropic_models_initialization_success(mock_getenv):
    """Test successful initialization of Anthropic models."""
    mock_getenv.return_value = "test-anthropic-key"
    
    with patch('src.models.model_manager.ChatOpenAI'), \
         patch('src.models.model_manager.ChatAnthropic') as mock_anthropic, \
         patch('src.models.model_manager.ChatCohere'), \
         patch('src.models.model_manager.genai'):
        
        manager = ModelManager()
        
        # Verify both Claude models were initialized
        assert mock_anthropic.call_count == 2
        
        # Verify models were registered
        assert "claude-2" in manager.models
        assert "claude-instant-1" in manager.models

@patch('os.getenv')
def test_anthropic_models_initialization_no_api_key(mock_getenv):
    """Test Anthropic models initialization when API key is missing."""
    mock_getenv.side_effect = lambda key: None if key == "ANTHROPIC_API_KEY" else "other-key"
    
    with patch('src.models.model_manager.ChatOpenAI'), \
         patch('src.models.model_manager.ChatAnthropic') as mock_anthropic, \
         patch('src.models.model_manager.ChatCohere'), \
         patch('src.models.model_manager.genai'):
        
        manager = ModelManager()
        
        # Verify no Anthropic models were initialized
        assert mock_anthropic.call_count == 0
        
        # Verify models were not registered
        assert "claude-2" not in manager.models
        assert "claude-instant-1" not in manager.models

@patch('os.getenv')
def test_anthropic_models_initialization_error(mock_getenv):
    """Test handling of errors during Anthropic models initialization."""
    mock_getenv.return_value = "test-anthropic-key"
    
    with patch('src.models.model_manager.ChatOpenAI'), \
         patch('src.models.model_manager.ChatAnthropic') as mock_anthropic, \
         patch('src.models.model_manager.ChatCohere'), \
         patch('src.models.model_manager.genai'):
        
        # Make ChatAnthropic raise an exception
        mock_anthropic.side_effect = Exception("Anthropic API Error")
        
        # Should not raise exception, but log error and continue
        manager = ModelManager()
        
        # Verify models were not registered
        assert "claude-2" not in manager.models
        assert "claude-instant-1" not in manager.models

def test_anthropic_model_parameters():
    """Test Anthropic model initialization parameters."""
    with patch('os.getenv') as mock_getenv, \
         patch('src.models.model_manager.ChatOpenAI'), \
         patch('src.models.model_manager.ChatAnthropic') as mock_anthropic, \
         patch('src.models.model_manager.ChatCohere'), \
         patch('src.models.model_manager.genai'):
        
        mock_getenv.return_value = "test-anthropic-key"
        manager = ModelManager()
        
        # Verify Claude-2 parameters
        claude2_call = mock_anthropic.call_args_list[0][1]
        assert claude2_call["model"] == "claude-2"
        assert claude2_call["temperature"] == 0.7
        assert claude2_call["max_tokens_to_sample"] == 2000
        assert claude2_call["anthropic_api_key"] == "test-anthropic-key"
        
        # Verify Claude-instant-1 parameters
        claude_instant_call = mock_anthropic.call_args_list[1][1]
        assert claude_instant_call["model"] == "claude-instant-1"
        assert claude_instant_call["temperature"] == 0.7
        assert claude_instant_call["max_tokens_to_sample"] == 2000
        assert claude_instant_call["anthropic_api_key"] == "test-anthropic-key" 