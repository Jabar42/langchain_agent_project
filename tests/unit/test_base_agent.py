"""Unit tests for the BaseAgent class."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.exceptions import ValidationError
from langchain.schema import BaseLanguageModel

class TestAgent(BaseAgent):
    """Test implementation of BaseAgent for testing abstract methods."""
    
    async def process_message(self, message: str) -> str:
        return f"Processed: {message}"
        
    async def handle_error(self, error: Exception) -> str:
        return f"Error handled: {str(error)}"
        
    async def validate_response(self, response: str) -> bool:
        return len(response) > 0

@pytest.fixture
def mock_llm():
    llm = Mock(spec=BaseLanguageModel)
    llm.agenerate = AsyncMock()
    return llm

@pytest.fixture
def agent(mock_llm):
    return TestAgent(mock_llm)

@pytest.mark.asyncio
async def test_process_message(agent):
    """Test basic message processing."""
    message = "Test message"
    response = await agent.process_message(message)
    assert response == "Processed: Test message"
    assert len(agent.get_history()) == 1

@pytest.mark.asyncio
async def test_handle_error(agent):
    """Test error handling."""
    error = ValueError("Test error")
    response = await agent.handle_error(error)
    assert response == "Error handled: Test error"

@pytest.mark.asyncio
async def test_validate_response(agent):
    """Test response validation."""
    valid_response = "Valid response"
    empty_response = ""
    
    assert await agent.validate_response(valid_response) is True
    assert await agent.validate_response(empty_response) is False

def test_add_to_history(agent):
    """Test conversation history management."""
    message = "Test message"
    response = "Test response"
    
    agent.add_to_history(message, response)
    history = agent.get_history()
    
    assert len(history) == 1
    assert history[0]["message"] == message
    assert history[0]["response"] == response
    assert isinstance(history[0]["timestamp"], str)

@pytest.mark.asyncio
async def test_llm_integration(agent, mock_llm):
    """Test integration with language model."""
    mock_llm.agenerate.return_value.generations[0][0].text = "Model response"
    
    # Configurar el modelo para una respuesta específica
    message = "Test message"
    await agent.process_message(message)
    
    # Verificar que el modelo fue llamado correctamente
    mock_llm.agenerate.assert_called_once()

@pytest.mark.asyncio
async def test_error_handling_flow(agent):
    """Test the complete error handling flow."""
    error = ValidationError("Invalid input")
    
    try:
        raise error
    except Exception as e:
        response = await agent.handle_error(e)
        
    assert "Error handled" in response
    assert "Invalid input" in response

@pytest.mark.asyncio
async def test_history_timestamp_format(agent):
    """Test that history timestamps are in ISO format."""
    message = "Test message"
    response = "Test response"
    
    agent.add_to_history(message, response)
    history = agent.get_history()
    
    # Verificar que el timestamp es una fecha ISO válida
    timestamp = history[0]["timestamp"]
    try:
        datetime.fromisoformat(timestamp)
        is_valid_date = True
    except ValueError:
        is_valid_date = False
        
    assert is_valid_date

@pytest.mark.asyncio
async def test_multiple_messages(agent):
    """Test handling multiple messages in sequence."""
    messages = ["Message 1", "Message 2", "Message 3"]
    
    for message in messages:
        await agent.process_message(message)
        
    history = agent.get_history()
    assert len(history) == len(messages)
    
    for i, message in enumerate(messages):
        assert history[i]["message"] == message
        assert history[i]["response"] == f"Processed: {message}" 