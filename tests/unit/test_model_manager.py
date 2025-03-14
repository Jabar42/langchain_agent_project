import pytest
from unittest.mock import Mock, patch
from src.models.model_manager import ModelManager
from src.utils.exceptions import ModelNotFoundError, ModelConfigError
from langchain.chat_models import ChatCohere
from src.models.model_tier import ModelTier

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

@pytest.fixture
def mock_cohere_api_key(monkeypatch):
    """Mock Cohere API key in environment."""
    monkeypatch.setenv("COHERE_API_KEY", "test-cohere-key")

def test_cohere_models_initialization(mock_cohere_api_key):
    """Test initialization of Cohere models."""
    with patch("langchain.chat_models.ChatCohere") as mock_cohere:
        manager = ModelManager()
        
        # Verify that ChatCohere was called for each model
        assert mock_cohere.call_count == 3
        
        # Verify model registrations
        assert "command-nightly" in manager.models
        assert "command-light-nightly" in manager.models
        assert "command-nightly-v2.0" in manager.models

def test_cohere_models_missing_api_key(monkeypatch):
    """Test handling of missing Cohere API key."""
    monkeypatch.delenv("COHERE_API_KEY", raising=False)
    
    with patch("structlog.get_logger") as mock_logger:
        manager = ModelManager()
        
        # Verify warning was logged
        mock_logger.return_value.warning.assert_any_call(
            "COHERE_API_KEY not found in environment, skipping Cohere models"
        )
        
        # Verify models were not registered
        assert "command-nightly" not in manager.models
        assert "command-light-nightly" not in manager.models
        assert "command-nightly-v2.0" not in manager.models

def test_cohere_model_configuration():
    """Test Cohere model configuration parameters."""
    with patch("os.getenv", return_value="test-cohere-key"), \
         patch("langchain.chat_models.ChatCohere") as mock_cohere:
        
        manager = ModelManager()
        
        # Verify configuration for command-nightly model
        mock_cohere.assert_any_call(
            model="command-nightly",
            temperature=0.7,
            max_tokens=2000,
            cohere_api_key="test-cohere-key"
        )
        
        # Verify configuration for command-light-nightly model
        mock_cohere.assert_any_call(
            model="command-light-nightly",
            temperature=0.7,
            max_tokens=2000,
            cohere_api_key="test-cohere-key"
        )
        
        # Verify configuration for command-nightly-v2.0 model
        mock_cohere.assert_any_call(
            model="command-nightly-v2.0",
            temperature=0.7,
            max_tokens=2000,
            cohere_api_key="test-cohere-key"
        )

def test_cohere_model_initialization_error():
    """Test error handling during Cohere model initialization."""
    with patch("os.getenv", return_value="test-cohere-key"), \
         patch("langchain.chat_models.ChatCohere", side_effect=Exception("Cohere API Error")), \
         patch("structlog.get_logger") as mock_logger:
        
        manager = ModelManager()
        
        # Verify error was logged
        mock_logger.return_value.error.assert_any_call(
            "Failed to initialize Cohere models: Cohere API Error"
        )
        
        # Verify models were not registered
        assert "command-nightly" not in manager.models
        assert "command-light-nightly" not in manager.models
        assert "command-nightly-v2.0" not in manager.models

@pytest.fixture
def mock_google_api_key(monkeypatch):
    """Mock Google API key in environment."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")

def test_google_models_initialization(mock_google_api_key):
    """Test initialization of Google models."""
    with patch("google.generativeai.configure") as mock_configure, \
         patch("google.generativeai.GenerativeModel") as mock_model:
        
        manager = ModelManager()
        
        # Verify API key configuration
        mock_configure.assert_called_once_with(api_key="test-google-key")
        
        # Verify model registrations
        assert mock_model.call_count >= 2  # At least Gemini Pro and Pro Vision
        assert "gemini-pro" in manager.models
        assert "gemini-pro-vision" in manager.models

def test_google_models_configuration():
    """Test Google model configuration parameters."""
    with patch("os.getenv", return_value="test-google-key"), \
         patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model:
        
        manager = ModelManager()
        
        # Verify configuration for gemini-pro model
        mock_model.assert_any_call(
            'gemini-pro',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        # Verify configuration for gemini-pro-vision model
        mock_model.assert_any_call(
            'gemini-pro-vision',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )

def test_google_models_missing_api_key(monkeypatch):
    """Test handling of missing Google API key."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    with patch("structlog.get_logger") as mock_logger:
        with pytest.raises(ModelConfigError) as exc_info:
            manager = ModelManager()
        
        assert str(exc_info.value) == "Error initializing default models: GOOGLE_API_KEY not found in environment"
        mock_logger.return_value.error.assert_any_call("GOOGLE_API_KEY not found in environment")

def test_google_ultra_model_unavailable():
    """Test handling of unavailable Gemini Ultra model."""
    with patch("os.getenv", return_value="test-google-key"), \
         patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model, \
         patch("structlog.get_logger") as mock_logger:
        
        # Make Ultra model raise an exception
        def mock_model_init(model_name, **kwargs):
            if model_name == 'gemini-ultra':
                raise Exception("Model not available")
            return Mock()
        
        mock_model.side_effect = mock_model_init
        
        manager = ModelManager()
        
        # Verify warning was logged
        mock_logger.return_value.warning.assert_any_call(
            "Gemini Ultra model not available: Model not available"
        )
        
        # Verify Ultra model was not registered but others were
        assert "gemini-ultra" not in manager.models
        assert "gemini-pro" in manager.models
        assert "gemini-pro-vision" in manager.models

def test_google_models_initialization_error():
    """Test error handling during Google models initialization."""
    with patch("os.getenv", return_value="test-google-key"), \
         patch("google.generativeai.configure", side_effect=Exception("Google API Error")), \
         patch("structlog.get_logger") as mock_logger:
        
        manager = ModelManager()
        
        # Verify error was logged
        mock_logger.return_value.error.assert_any_call(
            "Failed to initialize Google models: Google API Error"
        )
        
        # Verify no models were registered
        assert "gemini-pro" not in manager.models
        assert "gemini-pro-vision" not in manager.models
        assert "gemini-ultra" not in manager.models

def test_model_tiers():
    """Test model tier assignments."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = "test-key"
        manager = ModelManager()
        
        # Verify premium tier models
        assert manager.get_model_tier("gpt-4") == ModelTier.PREMIUM
        assert manager.get_model_tier("claude-2") == ModelTier.PREMIUM
        assert manager.get_model_tier("gemini-ultra") == ModelTier.PREMIUM
        
        # Verify advanced tier models
        assert manager.get_model_tier("gpt-3.5-turbo") == ModelTier.ADVANCED
        assert manager.get_model_tier("claude-instant-1") == ModelTier.ADVANCED
        assert manager.get_model_tier("command-nightly") == ModelTier.ADVANCED
        assert manager.get_model_tier("gemini-pro-vision") == ModelTier.ADVANCED
        
        # Verify standard tier models
        assert manager.get_model_tier("command-light-nightly") == ModelTier.STANDARD
        assert manager.get_model_tier("gemini-pro") == ModelTier.STANDARD
        
        # Verify basic tier models
        assert manager.get_model_tier("command-nightly-v2.0") == ModelTier.BASIC

def test_fallback_same_tier():
    """Test fallback to models in the same tier."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = "test-key"
        manager = ModelManager()
        
        # Make gpt-4 unavailable
        manager.models["gpt-4"].is_available = False
        
        # Should fallback to claude-2 (same tier)
        model_id, model = manager.get_model("gpt-4")
        assert model_id == "claude-2"
        assert model == manager.models["claude-2"].model

def test_fallback_lower_tier():
    """Test fallback to models in lower tiers."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = "test-key"
        manager = ModelManager()
        
        # Make all premium tier models unavailable
        for model_id in manager.fallback_chains[ModelTier.PREMIUM]:
            if model_id in manager.models:
                manager.models[model_id].is_available = False
        
        # Should fallback to advanced tier
        model_id, model = manager.get_model("gpt-4")
        assert model_id in manager.fallback_chains[ModelTier.ADVANCED]
        assert model == manager.models[model_id].model

def test_no_fallback():
    """Test behavior when fallback is disabled."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = "test-key"
        manager = ModelManager()
        
        # Make gpt-4 unavailable
        manager.models["gpt-4"].is_available = False
        
        # Should raise error when fallback is disabled
        with pytest.raises(ModelNotFoundError):
            manager.get_model("gpt-4", use_fallback=False)

def test_error_tracking():
    """Test error tracking and model availability."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = "test-key"
        manager = ModelManager()
        
        # Record errors for gpt-4
        for _ in range(3):
            manager.mark_model_error("gpt-4")
        
        # Model should be marked as unavailable
        assert not manager.models["gpt-4"].is_available
        
        # Reset model status
        manager.reset_model_status("gpt-4")
        
        # Model should be available again
        assert manager.models["gpt-4"].is_available
        assert manager.models["gpt-4"].error_count == 0

def test_list_available_models_by_tier():
    """Test listing available models filtered by tier."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = "test-key"
        manager = ModelManager()
        
        # Make some models unavailable
        manager.models["gpt-4"].is_available = False
        manager.models["command-nightly"].is_available = False
        
        # List premium tier models
        premium_models = manager.list_available_models(ModelTier.PREMIUM)
        assert "gpt-4" not in premium_models
        assert "claude-2" in premium_models
        
        # List advanced tier models
        advanced_models = manager.list_available_models(ModelTier.ADVANCED)
        assert "command-nightly" not in advanced_models
        assert "gpt-3.5-turbo" in advanced_models
        
        # List all available models
        all_models = manager.list_available_models()
        assert "gpt-4" not in all_models
        assert "command-nightly" not in all_models
        assert "claude-2" in all_models
        assert "gpt-3.5-turbo" in all_models

def test_best_available_model():
    """Test getting the best available model."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = "test-key"
        manager = ModelManager()
        
        # Make all premium models unavailable
        for model_id in manager.fallback_chains[ModelTier.PREMIUM]:
            if model_id in manager.models:
                manager.models[model_id].is_available = False
        
        # Get best available model
        model_id, model = manager._get_best_available_model()
        assert model_id in manager.fallback_chains[ModelTier.ADVANCED]
        assert model == manager.models[model_id].model
        
        # Make all models unavailable
        for model_info in manager.models.values():
            model_info.is_available = False
        
        # Should raise error when no models are available
        with pytest.raises(ModelNotFoundError):
            manager._get_best_available_model()

def test_nonexistent_model_fallback():
    """Test fallback behavior for nonexistent models."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = "test-key"
        manager = ModelManager()
        
        # Request nonexistent model with fallback
        model_id, model = manager.get_model("nonexistent-model")
        assert model_id in manager.models
        assert model == manager.models[model_id].model
        
        # Request nonexistent model without fallback
        with pytest.raises(ModelNotFoundError):
            manager.get_model("nonexistent-model", use_fallback=False) 