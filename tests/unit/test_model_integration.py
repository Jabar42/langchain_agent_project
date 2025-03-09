"""Unit tests for the model integration system."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.models.base import ModelIntegration
from src.models.openai import OpenAIIntegration
from src.models.anthropic import AnthropicIntegration
from src.utils.exceptions import ModelError

class TestModel(ModelIntegration):
    """Test implementation of ModelIntegration for testing."""
    
    async def generate_response(self, prompt: str) -> str:
        return f"Response to: {prompt}"
    
    async def validate_model_response(self, response: str) -> bool:
        return len(response) > 0
    
    def get_model_info(self) -> dict:
        return {
            "name": "test_model",
            "version": "1.0",
            "capabilities": ["text"]
        }

@pytest.fixture
def mock_openai():
    with patch("openai.AsyncOpenAI") as mock:
        client = Mock()
        client.chat.completions.create = AsyncMock()
        mock.return_value = client
        yield mock

@pytest.fixture
def mock_anthropic():
    with patch("anthropic.AsyncAnthropic") as mock:
        client = Mock()
        client.messages.create = AsyncMock()
        mock.return_value = client
        yield mock

@pytest.fixture
def test_model():
    return TestModel()

@pytest.mark.asyncio
async def test_basic_model_integration(test_model):
    """Test basic model integration functionality."""
    prompt = "Test prompt"
    response = await test_model.generate_response(prompt)
    assert response == f"Response to: {prompt}"
    assert await test_model.validate_model_response(response)

@pytest.mark.asyncio
async def test_openai_integration(mock_openai):
    """Test OpenAI model integration."""
    model = OpenAIIntegration()
    mock_response = Mock()
    mock_response.choices[0].message.content = "OpenAI response"
    mock_openai.return_value.chat.completions.create.return_value = mock_response
    
    response = await model.generate_response("Test prompt")
    assert response == "OpenAI response"
    mock_openai.return_value.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_anthropic_integration(mock_anthropic):
    """Test Anthropic model integration."""
    model = AnthropicIntegration()
    mock_response = Mock()
    mock_response.content[0].text = "Anthropic response"
    mock_anthropic.return_value.messages.create.return_value = mock_response
    
    response = await model.generate_response("Test prompt")
    assert response == "Anthropic response"
    mock_anthropic.return_value.messages.create.assert_called_once()

def test_model_info(test_model):
    """Test model information retrieval."""
    info = test_model.get_model_info()
    assert isinstance(info, dict)
    assert all(key in info for key in ["name", "version", "capabilities"])
    assert isinstance(info["capabilities"], list)

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in model integration."""
    model = TestModel()
    
    with pytest.raises(ModelError):
        # Simulate a model error
        with patch.object(model, 'generate_response', side_effect=ModelError("Model failed")):
            await model.generate_response("Test prompt")

@pytest.mark.asyncio
async def test_response_validation(test_model):
    """Test response validation."""
    valid_response = "Valid response"
    empty_response = ""
    
    assert await test_model.validate_model_response(valid_response)
    assert not await test_model.validate_model_response(empty_response)

@pytest.mark.asyncio
async def test_model_timeout():
    """Test model timeout handling."""
    model = TestModel()
    
    with pytest.raises(ModelError):
        with patch.object(model, 'generate_response', side_effect=TimeoutError):
            await model.generate_response("Test prompt")

@pytest.mark.asyncio
async def test_concurrent_requests(test_model):
    """Test handling of concurrent model requests."""
    import asyncio
    
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
    tasks = [test_model.generate_response(prompt) for prompt in prompts]
    
    responses = await asyncio.gather(*tasks)
    
    assert len(responses) == len(prompts)
    assert all(isinstance(response, str) for response in responses)

@pytest.mark.asyncio
async def test_model_rate_limiting():
    """Test model rate limiting behavior."""
    model = TestModel()
    requests = 5
    
    with patch.object(model, 'generate_response', AsyncMock()) as mock_generate:
        tasks = [model.generate_response(f"Prompt {i}") for i in range(requests)]
        await asyncio.gather(*tasks)
        
        assert mock_generate.call_count == requests

def test_model_capabilities(test_model):
    """Test model capabilities reporting."""
    info = test_model.get_model_info()
    capabilities = info["capabilities"]
    
    assert isinstance(capabilities, list)
    assert "text" in capabilities
    
    # Verify capability-specific functionality
    if "text" in capabilities:
        assert hasattr(test_model, "generate_response") 