"""Unit tests for the Threads connector."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.connectors.threads.threads_connector import ThreadsConnector
from src.agents.base_agent import BaseAgent

@pytest.fixture
def mock_agent():
    agent = Mock(spec=BaseAgent)
    agent.process_message = AsyncMock()
    return agent

@pytest.fixture
def connector(mock_agent):
    with patch("tweepy.Client"):
        return ThreadsConnector(agent=mock_agent, api_key="test_key")

@pytest.mark.asyncio
async def test_create_thread(connector, mock_agent):
    test_message = "Test thread message"
    mock_agent.process_message.return_value = {"response": "Agent response"}
    result = await connector.create_thread(test_message)
    assert "id" in result
    assert "created_at" in result
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0]["content"] == test_message
    mock_agent.process_message.assert_called_once_with(test_message)

@pytest.mark.asyncio
async def test_reply_to_thread(connector, mock_agent):
    thread_id = "test_thread_id"
    initial_message = "Initial message"
    reply_message = "Reply message"
    mock_agent.process_message.return_value = {"response": "Agent response"}
    await connector.create_thread(initial_message)
    mock_agent.process_message.reset_mock()
    mock_agent.process_message.return_value = {"response": "Reply response"}
    result = await connector.reply_to_thread(thread_id, reply_message)
    assert "content" in result
    assert "timestamp" in result
    assert "response" in result
    assert result["content"] == reply_message
    mock_agent.process_message.assert_called_once_with(reply_message)

def test_get_thread_history(connector):
    thread_id = "test_thread_id"
    messages = [
        {
            "content": "Message 1",
            "timestamp": datetime.now().isoformat(),
            "response": {"response": "Response 1"}
        },
        {
            "content": "Message 2",
            "timestamp": datetime.now().isoformat(),
            "response": {"response": "Response 2"}
        }
    ]
    connector.cache[thread_id] = {
        "id": thread_id,
        "created_at": datetime.now().isoformat(),
        "messages": messages
    }
    result = connector.get_thread_history(thread_id)
    assert result == messages
    assert len(result) == 2

def test_get_thread_history_not_found(connector):
    with pytest.raises(ValueError):
        connector.get_thread_history("nonexistent_thread")

def test_clear_cache(connector):
    thread_id = "test_thread_id"
    connector.cache[thread_id] = {
        "id": thread_id,
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    connector.clear_cache()
    assert len(connector.cache) == 0

@pytest.mark.asyncio
async def test_create_thread_error_handling(connector, mock_agent):
    mock_agent.process_message.side_effect = Exception("Test error")
    with pytest.raises(Exception):
        await connector.create_thread("Test message")

@pytest.mark.asyncio
async def test_reply_to_thread_error_handling(connector, mock_agent):
    thread_id = "test_thread_id"
    initial_message = "Initial message"
    mock_agent.process_message.return_value = {"response": "Agent response"}
    await connector.create_thread(initial_message)
    mock_agent.process_message.side_effect = Exception("Test error")
    with pytest.raises(Exception):
        await connector.reply_to_thread(thread_id, "Reply message")