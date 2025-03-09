"""Integration tests for platform connectors."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, Mock
from src.platforms.telegram import TelegramConnector
from src.platforms.threads import ThreadsConnector
from src.agents.multi_model_agent import MultiModelAgent
from src.models.openai import OpenAIIntegration
from src.evaluation.metrics import ResponseEvaluator
from src.utils.exceptions import PlatformError

@pytest.fixture
async def telegram_connector():
    """Create a TelegramConnector instance."""
    openai_model = OpenAIIntegration()
    evaluator = ResponseEvaluator()
    agent = MultiModelAgent(
        primary_model=openai_model,
        fallback_models=[],
        evaluator=evaluator
    )
    
    with patch('telegram.Bot') as mock_bot:
        connector = TelegramConnector(
            token="test_token",
            agent=agent
        )
        connector.bot = mock_bot
        return connector

@pytest.fixture
async def threads_connector():
    """Create a ThreadsConnector instance."""
    openai_model = OpenAIIntegration()
    evaluator = ResponseEvaluator()
    agent = MultiModelAgent(
        primary_model=openai_model,
        fallback_models=[],
        evaluator=evaluator
    )
    
    connector = ThreadsConnector(
        api_key="test_key",
        agent=agent
    )
    return connector

@pytest.mark.asyncio
async def test_telegram_message_flow(telegram_connector):
    """Test the complete message flow in Telegram."""
    # Mock update from Telegram
    mock_update = Mock()
    mock_message = Mock()
    mock_message.text = "Test message"
    mock_message.chat.id = 123
    mock_update.message = mock_message
    
    # Mock bot's send_message method
    telegram_connector.bot.send_message = AsyncMock()
    
    # Mock agent's process_message
    with patch.object(telegram_connector.agent, 'process_message', 
                     return_value="Agent response") as mock_process:
        await telegram_connector.handle_message(mock_update)
        
        # Verify message was processed
        mock_process.assert_called_once_with("Test message")
        
        # Verify response was sent
        telegram_connector.bot.send_message.assert_called_once_with(
            chat_id=123,
            text="Agent response"
        )

@pytest.mark.asyncio
async def test_threads_message_flow(threads_connector):
    """Test the complete message flow in Threads."""
    # Mock Threads API client
    with patch.object(threads_connector, 'api_client') as mock_client:
        mock_client.create_reply = AsyncMock()
        
        # Mock agent's process_message
        with patch.object(threads_connector.agent, 'process_message',
                         return_value="Agent response") as mock_process:
            await threads_connector.reply_to_thread(
                thread_id="123",
                message="Test message"
            )
            
            # Verify message was processed
            mock_process.assert_called_once_with("Test message")
            
            # Verify reply was created
            mock_client.create_reply.assert_called_once_with(
                thread_id="123",
                text="Agent response"
            )

@pytest.mark.asyncio
async def test_platform_error_handling(telegram_connector):
    """Test error handling in platform interactions."""
    mock_update = Mock()
    mock_message = Mock()
    mock_message.text = "Test message"
    mock_message.chat.id = 123
    mock_update.message = mock_message
    
    # Mock bot to raise an error
    telegram_connector.bot.send_message.side_effect = PlatformError("API Error")
    
    with pytest.raises(PlatformError):
        await telegram_connector.handle_message(mock_update)

@pytest.mark.asyncio
async def test_concurrent_platform_requests(telegram_connector):
    """Test handling multiple concurrent platform requests."""
    # Create multiple mock updates
    updates = []
    for i in range(3):
        mock_update = Mock()
        mock_message = Mock()
        mock_message.text = f"Message {i}"
        mock_message.chat.id = 123
        mock_update.message = mock_message
        updates.append(mock_update)
    
    # Mock bot's send_message
    telegram_connector.bot.send_message = AsyncMock()
    
    # Mock agent's process_message
    with patch.object(telegram_connector.agent, 'process_message') as mock_process:
        mock_process.side_effect = [f"Response {i}" for i in range(3)]
        
        # Process messages concurrently
        tasks = [telegram_connector.handle_message(update) for update in updates]
        await asyncio.gather(*tasks)
        
        assert mock_process.call_count == 3
        assert telegram_connector.bot.send_message.call_count == 3

@pytest.mark.asyncio
async def test_platform_authentication(threads_connector):
    """Test platform authentication flow."""
    # Mock authentication request
    with patch.object(threads_connector, 'api_client') as mock_client:
        mock_client.authenticate = AsyncMock()
        mock_client.authenticate.return_value = True
        
        is_authenticated = await threads_connector.authenticate()
        assert is_authenticated
        mock_client.authenticate.assert_called_once()

@pytest.mark.asyncio
async def test_platform_rate_limiting(telegram_connector):
    """Test platform rate limiting behavior."""
    mock_update = Mock()
    mock_message = Mock()
    mock_message.text = "Test message"
    mock_message.chat.id = 123
    mock_update.message = mock_message
    
    # Mock bot's send_message with rate limit error then success
    telegram_connector.bot.send_message = AsyncMock(side_effect=[
        PlatformError("Rate limit exceeded"),
        None  # Success after retry
    ])
    
    # Mock agent's process_message
    with patch.object(telegram_connector.agent, 'process_message',
                     return_value="Agent response"):
        # First attempt should fail with rate limit
        with pytest.raises(PlatformError):
            await telegram_connector.handle_message(mock_update)
        
        # Second attempt should succeed
        await asyncio.sleep(1)  # Simulate waiting for rate limit
        await telegram_connector.handle_message(mock_update)
        
        assert telegram_connector.bot.send_message.call_count == 2 