"""Base A2A Agent implementation for Stage 3 agents.

This module provides a base class for implementing A2A-compatible agents
that can serve Agent Cards, handle task requests, and communicate with
other agents.
"""

import json
import logging
import os
from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import Task, TaskState, Message as A2AMessage, Part as A2APart
from typing_extensions import override
import asyncio
import uuid
from .discovery import DiscoveryClient, AgentConnection

logger = logging.getLogger(__name__)


class BaseA2AAgent(AgentExecutor):
    """Base class for A2A-compatible agents with SMOL agent integration."""
    
    def __init__(
        self,
        agent_name: str,
        agent_description: str,
        agent_card_path: str,
        smol_agent: Any = None,
        capabilities: Optional[List[Dict[str, Any]]] = None
    ):
        """Initialize the A2A agent.
        
        Args:
            agent_name: Name of the agent
            agent_description: Description of the agent's purpose
            agent_card_path: Path to the agent's card JSON file
            smol_agent: Optional SMOL agent instance to wrap
            capabilities: Optional list of capability definitions
        """
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.agent_card_path = Path(agent_card_path)
        self.smol_agent = smol_agent
        self.capabilities = capabilities or []
        
        # Load agent card
        self.agent_card = self._load_agent_card()
        
        # Initialize capability handlers
        self.capability_handlers = {}
        self._register_capabilities()
        
        # Initialize discovery client
        self.discovery_client = DiscoveryClient(timeout=10)
        self.known_agents = {}  # Cache of discovered agents
        self.active_tasks = {}  # Track active async tasks
        
        logger.info(f"Initialized A2A agent: {self.agent_name}")
    
    def _load_agent_card(self) -> Dict[str, Any]:
        """Load the agent card from file."""
        if not self.agent_card_path.exists():
            logger.warning(f"Agent card not found at {self.agent_card_path}")
            return self._generate_default_card()
        
        try:
            with open(self.agent_card_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading agent card: {e}")
            return self._generate_default_card()
    
    def _generate_default_card(self) -> Dict[str, Any]:
        """Generate a default agent card."""
        # Determine host based on environment
        if os.getenv("DISCOVERY_METHOD") == "docker":
            # Use 0.0.0.0 for Docker environments
            host = "0.0.0.0"
        else:
            host = "localhost"
        
        port = os.getenv('A2A_PORT', '8000')
        
        return {
            "name": self.agent_name,
            "description": self.agent_description,
            "version": "1.0.0",
            "capabilities": self.capabilities,
            "endpoints": {
                "http": f"http://{host}:{port}/agent",
                "websocket": f"ws://{host}:{port}/ws"
            },
            "supported_protocols": ["a2a/1.0"],
            "metadata": {
                "created": datetime.now().isoformat(),
                "smol_agent": self.smol_agent is not None
            }
        }
    
    def _register_capabilities(self):
        """Register capability handlers.
        
        Subclasses should override this to register specific handlers.
        """
        # Default capability: get agent info
        self.register_capability("get_agent_info", self._handle_get_agent_info)
        
        # Discovery capabilities
        self.register_capability("discover_agents", self._handle_discover_agents)
        self.register_capability("query_agent", self._handle_query_agent)
        
        # Register custom capabilities from agent card
        for capability in self.agent_card.get("capabilities", []):
            cap_name = capability.get("name")
            if cap_name and not cap_name in self.capability_handlers:
                # Create a handler that delegates to SMOL agent or custom method
                self.register_capability(
                    cap_name,
                    lambda args, cap=capability: self._handle_capability(cap, args)
                )
    
    def register_capability(self, name: str, handler):
        """Register a capability handler.
        
        Args:
            name: Capability name
            handler: Function to handle the capability
        """
        self.capability_handlers[name] = handler
        logger.debug(f"Registered capability: {name}")
    
    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute an A2A task request.
        
        This method handles incoming task requests and routes them to
        appropriate capability handlers.
        """
        try:
            logger.debug(f"Execute called with context: {context}")
            logger.debug(f"Context type: {type(context)}")
            logger.debug(f"Context attributes: {[attr for attr in dir(context) if not attr.startswith('_')]}")
            
            # Get the user message from the context
            user_message = context.message
            logger.debug(f"User message: {user_message}")
            
            if not user_message:
                await event_queue.enqueue_event(
                    new_agent_text_message("No user message found in task")
                )
                return
            
            # Extract text from message parts
            text_content = ""
            structured_content = {}
            
            # Debug logging
            logger.debug(f"Message type: {type(user_message)}")
            logger.debug(f"Message parts: {user_message.parts}")
            
            for i, part in enumerate(user_message.parts):
                logger.debug(f"Part {i}: type={type(part)}")
                
                # Use model_dump() to get the actual content
                if hasattr(part, 'model_dump'):
                    part_data = part.model_dump()
                    logger.debug(f"Part {i} data: {part_data}")
                    
                    # Extract text or data from the dumped model
                    if 'text' in part_data and part_data['text']:
                        text_content = part_data['text']
                        logger.debug(f"Found text: {text_content}")
                    elif 'data' in part_data and part_data['data']:
                        structured_content = part_data['data']
                        logger.debug(f"Found data: {structured_content}")
                    
                # Alternative: Access via root attribute
                elif hasattr(part, 'root'):
                    part_content = part.root
                    logger.debug(f"Part {i} root: {part_content}")
                    
                    if hasattr(part_content, 'text') and part_content.text:
                        text_content = part_content.text
                        logger.debug(f"Found text in root: {text_content}")
                    elif hasattr(part_content, 'data') and part_content.data:
                        structured_content = part_content.data
                        logger.debug(f"Found data in root: {structured_content}")
            
            # Process the message
            if text_content:
                # Simple text query - delegate to SMOL agent if available
                if self.smol_agent:
                    result = await self._execute_with_smol_agent(text_content)
                else:
                    result = await self._handle_text_query(text_content)
            elif structured_content:
                # Structured message - look for capability invocation
                result = await self._handle_structured_message(structured_content)
            else:
                result = "No processable content found in message"
            
            # Send the result
            if isinstance(result, dict):
                # Convert dict to JSON string for now
                await event_queue.enqueue_event(new_agent_text_message(json.dumps(result)))
            else:
                await event_queue.enqueue_event(new_agent_text_message(str(result)))
                
        except Exception as e:
            logger.error(f"Error in A2A execution: {e}")
            await event_queue.enqueue_event(
                new_agent_text_message(f"Error processing request: {str(e)}")
            )
    
    async def _execute_with_smol_agent(self, query: str) -> str:
        """Execute a query using the wrapped SMOL agent.
        
        Uses appropriate timeouts based on query complexity.
        """
        # Check if this is a simple query we can handle quickly
        simple_queries = ['hello', 'help', 'what can you do', 'capabilities']
        is_simple = any(simple in query.lower() for simple in simple_queries)
        
        # Set timeout based on query complexity
        timeout = 10.0 if is_simple else 50.0  # 10s for simple, 50s for complex
        
        try:
            logger.info(f"Executing query with {timeout}s timeout: {query[:50]}...")
            
            # Check if the run method is async
            if asyncio.iscoroutinefunction(self.smol_agent.run):
                # If it's async, call it directly
                result = await asyncio.wait_for(
                    self.smol_agent.run(query),
                    timeout=timeout
                )
            else:
                # If it's sync, run it in a thread
                result = await asyncio.wait_for(
                    asyncio.to_thread(self.smol_agent.run, query),
                    timeout=timeout
                )
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Query timed out after {timeout}s: {query}")
            return "Request timed out. Please try a simpler query."
        except Exception as e:
            logger.error(f"SMOL agent execution error: {e}")
            return f"Error executing query: {str(e)}"
    
    async def _handle_text_query(self, query: str) -> str:
        """Handle a text query when no SMOL agent is available.
        
        Subclasses should override this method.
        """
        return f"{self.agent_name} received query: {query}"
    
    async def _handle_structured_message(self, content: Dict[str, Any]) -> Any:
        """Handle a structured message, typically a capability invocation."""
        # Look for capability invocation
        capability = content.get("capability")
        if capability and capability in self.capability_handlers:
            args = content.get("args", {})
            handler = self.capability_handlers[capability]
            return await self._call_handler(handler, args)
        
        # If no specific capability, treat as general query
        query = content.get("query", "")
        if query and self.smol_agent:
            return await self._execute_with_smol_agent(query)
        
        return {"error": "No recognized capability or query in message"}
    
    async def _call_handler(self, handler, args: Dict[str, Any]) -> Any:
        """Call a handler function, handling both sync and async."""
        import asyncio
        if asyncio.iscoroutinefunction(handler):
            return await handler(args)
        else:
            return handler(args)
    
    def _handle_get_agent_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_agent_info capability."""
        return {
            "name": self.agent_name,
            "description": self.agent_description,
            "capabilities": [
                cap["name"] for cap in self.agent_card.get("capabilities", [])
            ],
            "version": self.agent_card.get("version", "1.0.0")
        }
    
    async def _handle_capability(self, capability: Dict[str, Any], args: Dict[str, Any]) -> Any:
        """Generic handler for capabilities defined in agent card."""
        cap_name = capability.get("name")
        
        # If we have a SMOL agent, try to use it
        if self.smol_agent:
            # Format the request as a natural language query
            query_parts = [f"Please {capability.get('description', cap_name)}"]
            for key, value in args.items():
                query_parts.append(f"{key}: {value}")
            query = " ".join(query_parts)
            
            return await self._execute_with_smol_agent(query)
        
        # Otherwise, return a not implemented response
        return {
            "error": f"Capability '{cap_name}' not implemented",
            "capability": cap_name,
            "args": args
        }
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Get the agent's card."""
        return self.agent_card
    
    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel the current task execution.
        
        This method is called when a task cancellation is requested.
        Most simple agents don't support cancellation.
        """
        await event_queue.enqueue_event(
            new_agent_text_message("Task cancellation is not supported by this agent")
        )
    
    def _should_use_async_task(self, query: str) -> bool:
        """Determine if a query should be processed asynchronously.
        
        Args:
            query: The user's query
            
        Returns:
            True if the query should be processed as an async task
        """
        # Simple heuristics for now
        simple_queries = ['hello', 'help', 'what can you do', 'capabilities', 'hi']
        return not any(simple in query.lower() for simple in simple_queries)
    
    async def _start_async_task(self, query: str, context: RequestContext, event_queue: EventQueue) -> str:
        """Start processing a query as an async task.
        
        Args:
            query: The user's query
            context: Request context
            event_queue: Event queue for updates
            
        Returns:
            Initial response indicating task creation
        """
        # Create a task ID
        task_id = str(uuid.uuid4())
        
        # Send initial response
        await event_queue.enqueue_event(
            new_agent_text_message(
                f"Your request has been received and is being processed.\n"
                f"Task ID: {task_id}\n"
                f"This may take a few moments..."
            )
        )
        
        # Start async processing in background
        asyncio.create_task(self._process_async_query(query, task_id, context))
        
        return f"Processing started with task ID: {task_id}"
    
    async def _process_async_query(self, query: str, task_id: str, context: RequestContext):
        """Process a query asynchronously in the background.
        
        Args:
            query: The user's query
            task_id: Task identifier
            context: Request context
        """
        try:
            # Check if the run method is async
            if asyncio.iscoroutinefunction(self.smol_agent.run):
                # If it's async, call it directly
                result = await asyncio.wait_for(
                    self.smol_agent.run(query),
                    timeout=60.0  # 60 second timeout for complex queries
                )
            else:
                # Run the SMOL agent in a thread with longer timeout
                result = await asyncio.wait_for(
                    asyncio.to_thread(self.smol_agent.run, query),
                    timeout=60.0  # 60 second timeout for complex queries
                )
            
            # Store result in the active tasks
            self.active_tasks[task_id] = {
                "status": "completed",
                "result": result,
                "completed_at": datetime.now().isoformat()
            }
            
            logger.info(f"Task {task_id} completed successfully")
            logger.info(f"Result: {result[:200]}...")
            
        except asyncio.TimeoutError:
            logger.error(f"Task {task_id} timed out after 60 seconds")
            self.active_tasks[task_id] = {
                "status": "failed",
                "error": "Request timed out after 60 seconds",
                "completed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            self.active_tasks[task_id] = {
                "status": "failed", 
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    @abstractmethod
    def setup_custom_capabilities(self):
        """Setup custom capabilities for the specific agent.
        
        Subclasses must implement this to register their specific capabilities.
        """
        pass
    
    async def _handle_discover_agents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent discovery requests."""
        capability = args.get("capability")
        refresh = args.get("refresh", False)
        
        if refresh:
            self.discovery_client.clear_cache()
        
        # Discover agents
        agents = await self.discovery_client.discover_agents_on_ports()
        
        # Cache discovered agents
        for agent in agents:
            name = agent.get("name")
            if name:
                self.known_agents[name] = agent
        
        # Filter by capability if requested
        if capability:
            agents = [
                agent for agent in agents
                if capability in [cap.get("name") for cap in agent.get("capabilities", [])]
            ]
        
        return {
            "agents": [
                {
                    "name": agent.get("name"),
                    "description": agent.get("description"),
                    "capabilities": [cap.get("name") for cap in agent.get("capabilities", [])],
                    "endpoint": agent.get("_discovered_at")
                }
                for agent in agents
            ],
            "count": len(agents)
        }
    
    async def _handle_query_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests to query another agent."""
        target_agent = args.get("agent_name")
        query = args.get("query")
        capability = args.get("capability")
        capability_args = args.get("capability_args", {})
        
        if not target_agent:
            return {"error": "agent_name is required"}
        
        if not query and not capability:
            return {"error": "Either query or capability must be provided"}
        
        # Find the agent
        agent_card = self.known_agents.get(target_agent)
        if not agent_card:
            # Try to discover
            await self._handle_discover_agents({"refresh": True})
            agent_card = self.known_agents.get(target_agent)
        
        if not agent_card:
            return {"error": f"Agent '{target_agent}' not found"}
        
        # Connect to the agent
        connection = AgentConnection(agent_card)
        
        try:
            if capability:
                # Invoke specific capability
                response = await connection.invoke_capability(capability, capability_args)
            else:
                # Send general query
                response = await connection.send_task(query)
            
            return {
                "agent": target_agent,
                "response": response,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error querying agent {target_agent}: {e}")
            return {
                "error": str(e),
                "agent": target_agent,
                "success": False
            }
    
    async def query_other_agent(
        self,
        agent_name: str,
        query: Optional[str] = None,
        capability: Optional[str] = None,
        capability_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convenience method to query another agent.
        
        Args:
            agent_name: Name of the target agent
            query: Natural language query (if not using capability)
            capability: Specific capability to invoke
            capability_args: Arguments for the capability
            
        Returns:
            Response from the other agent
        """
        return await self._handle_query_agent({
            "agent_name": agent_name,
            "query": query,
            "capability": capability,
            "capability_args": capability_args or {}
        })