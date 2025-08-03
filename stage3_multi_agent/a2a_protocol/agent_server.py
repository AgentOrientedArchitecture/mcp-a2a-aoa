"""A2A Agent Server implementation.

This module provides the server component that hosts A2A agents,
handling HTTP and WebSocket endpoints for agent communication.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

logger = logging.getLogger(__name__)


class A2AAgentServer:
    """Server for hosting A2A agents with agent card serving."""
    
    def __init__(
        self,
        agent_executor: AgentExecutor,
        agent_card_path: str,
        host: str = "0.0.0.0",
        port: int = 8000,
        server_name: Optional[str] = None
    ):
        """Initialize the A2A server.
        
        Args:
            agent_executor: The agent executor to host
            agent_card_path: Path to the agent's card JSON file
            host: Host to bind to
            port: Port to bind to
            server_name: Optional server name
        """
        self.agent_executor = agent_executor
        self.agent_card_path = Path(agent_card_path)
        self.host = host
        self.port = port
        self.server_name = server_name or f"a2a-agent-{port}"
        
        # Load agent card
        self.agent_card = self._load_agent_card()
        
        # Create task store
        self.task_store = InMemoryTaskStore()
        
        # Create request handler
        self.request_handler = DefaultRequestHandler(
            agent_executor=self.agent_executor,
            task_store=self.task_store
        )
        
        # Create A2A Starlette application
        self.a2a_app = A2AStarletteApplication(
            agent_card=self.agent_card,
            http_handler=self.request_handler  # Note: parameter is named http_handler
        )
        
        # Build the actual ASGI application
        self.app = self.a2a_app.build()
        
        logger.info(f"Initialized A2A server: {self.server_name} on {host}:{port}")
    
    def _load_agent_card(self) -> AgentCard:
        """Load the agent card from file."""
        if self.agent_card_path.exists():
            try:
                with open(self.agent_card_path, 'r') as f:
                    card_data = json.load(f)
                    
                # Convert capabilities list to AgentSkill objects
                skills = []
                for cap in card_data.get("capabilities", []):
                    skill = AgentSkill(
                        id=cap.get("name", "unknown"),
                        name=cap.get("name", "Unknown"),
                        description=cap.get("description", ""),
                        tags=cap.get("tags", []),
                        examples=cap.get("examples", [])
                    )
                    skills.append(skill)
                
                # Create AgentCard
                return AgentCard(
                    name=card_data.get("name", self.server_name),
                    description=card_data.get("description", "A2A Agent"),
                    version=card_data.get("version", "1.0.0"),
                    url=f"http://{self.host}:{self.port}/",
                    default_input_modes=["text"],
                    default_output_modes=["text"],
                    capabilities=AgentCapabilities(
                        streaming=card_data.get("capabilities_config", {}).get("streaming", False),
                        push_notifications=card_data.get("capabilities_config", {}).get("push_notifications", False)
                    ),
                    skills=skills
                )
            except Exception as e:
                logger.error(f"Error loading agent card: {e}")
        
        # Get card from agent executor if it has one
        if hasattr(self.agent_executor, 'get_agent_card'):
            card_data = self.agent_executor.get_agent_card()
            # Convert dict to AgentCard
            skills = []
            for cap in card_data.get("capabilities", []):
                skill = AgentSkill(
                    id=cap.get("name", "unknown"),
                    name=cap.get("name", "Unknown"),
                    description=cap.get("description", ""),
                    tags=cap.get("tags", []),
                    examples=cap.get("examples", [])
                )
                skills.append(skill)
            
            return AgentCard(
                name=card_data.get("name", self.server_name),
                description=card_data.get("description", "A2A Agent"),
                version=card_data.get("version", "1.0.0"),
                url=f"http://{self.host}:{self.port}/",
                default_input_modes=["text"],
                default_output_modes=["text"],
                capabilities=AgentCapabilities(streaming=False),
                skills=skills
            )
        
        # Return minimal card
        return AgentCard(
            name=self.server_name,
            description="A2A Agent",
            version="1.0.0",
            url=f"http://{self.host}:{self.port}/",
            default_input_modes=["text"],
            default_output_modes=["text"],
            capabilities=AgentCapabilities(streaming=False),
            skills=[]
        )
    
    def run(self):
        """Run the server using uvicorn."""
        try:
            logger.info(f"Starting A2A server on {self.host}:{self.port}")
            # Note: self.app is the built Starlette instance from A2AStarletteApplication.build()
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise


def create_and_run_agent_server(
    agent_executor: AgentExecutor,
    agent_card_path: str,
    host: str = "0.0.0.0",
    port: Optional[int] = None,
    server_name: Optional[str] = None
):
    """Convenience function to create and run an A2A agent server.
    
    Args:
        agent_executor: The agent executor to host
        agent_card_path: Path to the agent's card JSON file
        host: Host to bind to
        port: Port to bind to (defaults from env or 8000)
        server_name: Optional server name
    """
    if port is None:
        port = int(os.getenv("A2A_PORT", "8000"))
    
    server = A2AAgentServer(
        agent_executor=agent_executor,
        agent_card_path=agent_card_path,
        host=host,
        port=port,
        server_name=server_name
    )
    
    server.run()