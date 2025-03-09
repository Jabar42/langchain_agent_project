"""Threads Connector for interacting with the Threads API."""

import os
from typing import Dict, List, Optional, Any
import tweepy
from datetime import datetime
import logging
import json
import aiohttp
import asyncio
from ...agents.base_agent import BaseAgent
from ...utils.exceptions import ThreadsError, AuthenticationError

logger = logging.getLogger(__name__)

class ThreadsConnector:
    """Connector for interacting with the Threads API."""
    
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.session = None
        self.auth_token = None
        self.device_id = None
        self.username = None
        self.cache = {}
        self._load_credentials()
        
    def _load_credentials(self):
        """Load credentials from environment variables."""
        self.username = os.getenv("THREADS_USERNAME")
        self.password = os.getenv("THREADS_PASSWORD")
        self.device_id = os.getenv("THREADS_DEVICE_ID")
        
        if not all([self.username, self.password, self.device_id]):
            raise AuthenticationError("Missing required Threads credentials")
            
    async def _setup_session(self):
        """Setup aiohttp session and authenticate."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            await self._authenticate()
            
    async def _authenticate(self):
        """Authenticate with Threads API."""
        try:
            auth_url = "https://www.threads.net/api/v1/web/accounts/login"
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/json",
                "X-Device-ID": self.device_id
            }
            
            data = {
                "username": self.username,
                "password": self.password,
                "device_id": self.device_id
            }
            
            async with self.session.post(auth_url, json=data, headers=headers) as response:
                if response.status != 200:
                    raise AuthenticationError(f"Failed to authenticate: {await response.text()}")
                    
                result = await response.json()
                self.auth_token = result.get("token")
                if not self.auth_token:
                    raise AuthenticationError("No auth token received")
                    
                logger.info("Successfully authenticated with Threads")
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(f"Failed to authenticate: {str(e)}")
            
    async def create_thread(self, initial_message: str) -> Dict[str, Any]:
        """Create a new thread with an initial message."""
        await self._setup_session()
        
        try:
            # Procesar mensaje con el agente
            response = await self.agent.process_message(initial_message)
            
            # Crear thread en Threads
            thread_url = "https://www.threads.net/api/v1/web/threads/create"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "text": response["best_response"],
                "mentioned_users": [],
                "reply_settings": "everyone"
            }
            
            async with self.session.post(thread_url, json=data, headers=headers) as resp:
                if resp.status != 200:
                    raise ThreadsError(f"Failed to create thread: {await resp.text()}")
                    
                result = await resp.json()
                thread_id = result["thread"]["id"]
                
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
            logger.error(f"Failed to create thread: {str(e)}")
            raise ThreadsError(f"Failed to create thread: {str(e)}")
            
    async def reply_to_thread(self, thread_id: str, message: str) -> Dict[str, Any]:
        """Reply to an existing thread."""
        await self._setup_session()
        
        if thread_id not in self.cache:
            raise ValueError(f"Thread {thread_id} not found")
            
        try:
            # Procesar respuesta con el agente
            response = await self.agent.process_message(message)
            
            # Publicar respuesta en Threads
            reply_url = f"https://www.threads.net/api/v1/web/threads/{thread_id}/reply"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "text": response["best_response"],
                "mentioned_users": [],
                "reply_settings": "everyone"
            }
            
            async with self.session.post(reply_url, json=data, headers=headers) as resp:
                if resp.status != 200:
                    raise ThreadsError(f"Failed to reply to thread: {await resp.text()}")
                    
                reply_info = {
                    "content": message,
                    "timestamp": datetime.now().isoformat(),
                    "response": response
                }
                
                self.cache[thread_id]["messages"].append(reply_info)
                logger.info(f"Added reply to thread {thread_id}")
                return reply_info
                
        except Exception as e:
            logger.error(f"Failed to reply to thread: {str(e)}")
            raise ThreadsError(f"Failed to reply to thread: {str(e)}")
            
    async def get_thread_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get the history of a thread including all messages and responses."""
        await self._setup_session()
        
        if thread_id not in self.cache:
            try:
                # Obtener historial de Threads
                history_url = f"https://www.threads.net/api/v1/web/threads/{thread_id}/history"
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                async with self.session.get(history_url, headers=headers) as resp:
                    if resp.status != 200:
                        raise ThreadsError(f"Failed to get thread history: {await resp.text()}")
                        
                    history = await resp.json()
                    self.cache[thread_id] = {
                        "id": thread_id,
                        "messages": history["messages"]
                    }
                    
            except Exception as e:
                logger.error(f"Failed to get thread history: {str(e)}")
                raise ThreadsError(f"Failed to get thread history: {str(e)}")
                
        return self.cache[thread_id]["messages"]
        
    def clear_cache(self):
        """Clear the local cache of thread data."""
        self.cache = {}
        logger.info("Thread cache cleared")
        
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
            self.auth_token = None