"""Threads Connector for interacting with the Threads API."""

import os
from typing import Dict, List, Optional, Any
import tweepy
from datetime import datetime
import logging
from ...agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ThreadsConnector:
    def __init__(self, agent: BaseAgent, api_key: Optional[str] = None):
        self.agent = agent
        self.cache = {}
        self._setup_client(api_key)

    def _setup_client(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv("THREADS_API_KEY")
        if not api_key:
            raise ValueError("Threads API key not provided and THREADS_API_KEY not found in environment")
        try:
            self.client = tweepy.Client(api_key)
            logger.info("Successfully initialized Threads API client")
        except Exception as e:
            logger.error(f"Failed to initialize Threads API client: {e}")
            raise

    async def create_thread(self, initial_message: str) -> Dict[str, Any]:
        try:
            response = await self.agent.process_message(initial_message)
            thread_id = "placeholder_thread_id"
            thread_info = {
                "id": thread_id,
                "created_at": datetime.now().isoformat(),
                "messages": [{
                    "content": initial_message,
                    "timestamp": datetime.now().isoformat(),
                    "response": response
                }]
            }
            self.cache[thread_id] = thread_info
            logger.info(f"Created new thread with ID: {thread_id}")
            return thread_info
        except Exception as e:
            logger.error(f"Failed to create thread: {e}")
            raise

    async def reply_to_thread(self, thread_id: str, message: str) -> Dict[str, Any]:
        if thread_id not in self.cache:
            raise ValueError(f"Thread {thread_id} not found")
        try:
            response = await self.agent.process_message(message)
            reply_info = {
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "response": response
            }
            self.cache[thread_id]["messages"].append(reply_info)
            logger.info(f"Added reply to thread {thread_id}")
            return reply_info
        except Exception as e:
            logger.error(f"Failed to reply to thread {thread_id}: {e}")
            raise

    def get_thread_history(self, thread_id: str) -> List[Dict[str, Any]]:
        if thread_id not in self.cache:
            raise ValueError(f"Thread {thread_id} not found")
        return self.cache[thread_id]["messages"]

    def clear_cache(self):
        self.cache = {}
        logger.info("Thread cache cleared")