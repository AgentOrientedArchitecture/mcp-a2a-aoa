"""Enhanced Base A2A Agent with Comprehensive Telemetry.

This module provides an enhanced base class for implementing A2A-compatible agents
with comprehensive OpenTelemetry instrumentation for observability and monitoring.
"""

import json
import logging
import os
import time
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
from telemetry import TelemetryManager

logger = logging.getLogger(__name__)


class EnhancedBaseA2AAgent(AgentExecutor):
    """Enhanced base class for A2A-compatible agents with comprehensive telemetry."""
    
    def __init__(
        self,
        agent_name: str,
        agent_description: str,
        agent_card_path: str,
        smol_agent: Any = None,
        capabilities: Optional[List[Dict[str, Any]]] = None,
        enable_telemetry: bool = True,
        phoenix_endpoint: Optional[str] = None
    ):
        """Initialize the enhanced A2A agent.
        
        Args:
            agent_name: Name of the agent
            agent_description: Description of the agent's purpose
            agent_card_path: Path to the agent's card JSON file
            smol_agent: Optional SMOL agent instance to wrap
            capabilities: Optional list of capability definitions
            enable_telemetry: Whether to enable telemetry
            phoenix_endpoint: Phoenix collector endpoint URL
        """
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.agent_card_path = Path(agent_card_path)
        self.smol_agent = smol_agent
        self.capabilities = capabilities or []
        self.enable_telemetry = enable_telemetry
        
        # Initialize telemetry if enabled
        if self.enable_telemetry:
            self.telemetry = TelemetryManager(
                phoenix_endpoint=phoenix_endpoint,
                project_name="a2a-multi-agent"
            )
            logger.info(f"Telemetry initialized for agent: {agent_name}")
        else:
            self.telemetry = None
            logger.info(f"Telemetry disabled for agent: {agent_name}")
        
        # Load agent card
        self.agent_card = self._load_agent_card()
        
        # Initialize capability handlers
        self.capability_handlers = {}
        self._register_capabilities()
        
        # Initialize discovery client
        self.discovery_client = DiscoveryClient(timeout=10)
        self.known_agents = {}  # Cache of discovered agents
        self.active_tasks = {}  # Track active async tasks
        
        logger.info(f"Initialized Enhanced A2A agent: {self.agent_name}")
    
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
        }
    
    def _register_capabilities(self):
        """Register capability handlers."""
        # Register default capabilities
        self.register_capability("get_agent_info", self._handle_get_agent_info)
        self.register_capability("discover_agents", self._handle_discover_agents)
        self.register_capability("query_agent", self._handle_query_agent)
        
        # Register custom capabilities
        self.setup_custom_capabilities()
    
    def register_capability(self, name: str, handler):
        """Register a capability handler."""
        self.capability_handlers[name] = handler
        logger.debug(f"Registered capability: {name}")
    
    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Enhanced execute with comprehensive telemetry."""
        start_time = time.time()
        execution_id = str(uuid.uuid4())
        
        # Create execution span
        if self.telemetry:
            with self.telemetry.get_a2a_telemetry().trace_task_execution(
                self.agent_name, execution_id, "execute"
            ) as span:
                try:
                    # Extract query from context
                    query = self._extract_query(context)
                    
                    # Trace the query
                    if self.telemetry:
                        span.set_attribute("query.text", query)
                        span.set_attribute("query.length", len(query))
                    
                    # Execute the query
                    result = await self._execute_with_telemetry(query, context, event_queue)
                    
                    # Record success
                    duration = time.time() - start_time
                    if self.telemetry:
                        span.set_attribute("execution.status", "success")
                        span.set_attribute("execution.duration_ms", duration * 1000)
                        span.set_attribute("result.length", len(str(result)))
                    
                    # Send result
                    await self._send_result(context, event_queue, result)
                    
                except Exception as e:
                    # Record error
                    duration = time.time() - start_time
                    if self.telemetry:
                        span.set_attribute("execution.status", "error")
                        span.set_attribute("execution.error", str(e))
                        span.set_attribute("execution.error_type", type(e).__name__)
                        span.set_attribute("execution.duration_ms", duration * 1000)
                    
                    logger.error(f"Execution error: {e}")
                    await self._send_error(context, event_queue, str(e))
        else:
            # Fallback without telemetry
            try:
                query = self._extract_query(context)
                result = await self._execute_without_telemetry(query, context, event_queue)
                await self._send_result(context, event_queue, result)
            except Exception as e:
                logger.error(f"Execution error: {e}")
                await self._send_error(context, event_queue, str(e))
    
    async def _execute_with_telemetry(self, query: str, context: RequestContext, event_queue: EventQueue):
        """Execute query with telemetry instrumentation."""
        # Determine if this is a complex query that needs async handling
        if self._should_use_async_task(query):
            return await self._start_async_task(query, context, event_queue)
        
        # Handle structured message
        if self._is_structured_message(query):
            return await self._handle_structured_message_with_telemetry(query)
        
        # Handle text query
        return await self._handle_text_query_with_telemetry(query)
    
    async def _execute_without_telemetry(self, query: str, context: RequestContext, event_queue: EventQueue):
        """Execute query without telemetry (fallback)."""
        if self._should_use_async_task(query):
            return await self._start_async_task(query, context, event_queue)
        
        if self._is_structured_message(query):
            return await self._handle_structured_message(query)
        
        return await self._handle_text_query(query)
    
    async def _handle_text_query_with_telemetry(self, query: str) -> str:
        """Handle text query with telemetry."""
        if self.telemetry:
            with self.telemetry.get_smol_telemetry().create_agent_span(
                self.agent_name, "text_query", query_text=query
            ) as span:
                try:
                    if self.smol_agent:
                        result = await self._execute_with_smol_agent(query)
                    else:
                        result = await self._handle_text_query(query)
                    
                    span.set_attribute("result.length", len(str(result)))
                    return result
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            if self.smol_agent:
                return await self._execute_with_smol_agent(query)
            else:
                return await self._handle_text_query(query)
    
    async def _handle_structured_message_with_telemetry(self, content: Dict[str, Any]) -> Any:
        """Handle structured message with telemetry."""
        if self.telemetry:
            with self.telemetry.get_a2a_telemetry().create_span_with_context(
                "a2a.structured_message",
                agent_name=self.agent_name,
                message_type=content.get("type", "unknown")
            ) as span:
                try:
                    result = await self._handle_structured_message(content)
                    span.set_attribute("result.type", type(result).__name__)
                    return result
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            return await self._handle_structured_message(content)
    
    async def _execute_with_smol_agent(self, query: str) -> str:
        """Execute query using SMOL agent with telemetry."""
        if self.telemetry:
            with self.telemetry.get_smol_telemetry().create_agent_span(
                self.agent_name, "smol_execution", query_text=query
            ) as span:
                try:
                    # Execute with SMOL agent - handle both sync and async
                    if hasattr(self.smol_agent, 'run'):
                        if asyncio.iscoroutinefunction(self.smol_agent.run):
                            # Async run method
                            result = await self.smol_agent.run(query)
                        else:
                            # Sync run method - run in thread pool
                            result = await asyncio.to_thread(self.smol_agent.run, query)
                    else:
                        # Fallback for agents without run method
                        result = f"Agent {self.agent_name} executed query: {query}"
                    
                    span.set_attribute("result.length", len(str(result)))
                    return result
                except Exception as e:
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        else:
            # Execute without telemetry
            if hasattr(self.smol_agent, 'run'):
                if asyncio.iscoroutinefunction(self.smol_agent.run):
                    # Async run method
                    return await self.smol_agent.run(query)
                else:
                    # Sync run method - run in thread pool
                    return await asyncio.to_thread(self.smol_agent.run, query)
            else:
                # Fallback for agents without run method
                return f"Agent {self.agent_name} executed query: {query}"
    
    async def _handle_text_query(self, query: str) -> str:
        """Handle text query (to be overridden by subclasses)."""
        return f"Text query received: {query}"
    
    async def _handle_structured_message(self, content: Dict[str, Any]) -> Any:
        """Handle structured message (to be overridden by subclasses)."""
        return f"Structured message received: {content}"
    
    def _extract_query(self, context: RequestContext) -> str:
        """Extract query from context."""
        try:
            # Handle A2A message structure
            if hasattr(context, 'message') and context.message:
                if hasattr(context.message, 'parts') and context.message.parts:
                    parts = context.message.parts
                    if parts and hasattr(parts[0], 'text'):
                        return parts[0].text
                    elif parts and hasattr(parts[0], 'model_dump'):
                        part_data = parts[0].model_dump()
                        if 'text' in part_data and part_data['text']:
                            return part_data['text']
            
            # Fallback to task content
            if hasattr(context, 'task') and context.task:
                if hasattr(context.task, 'content') and context.task.content:
                    return context.task.content
            
            return "No query found"
        except Exception as e:
            logger.error(f"Error extracting query: {e}")
            return "Error extracting query"
    
    def _is_structured_message(self, query: str) -> bool:
        """Check if query is a structured message."""
        try:
            content = json.loads(query)
            return isinstance(content, dict)
        except (json.JSONDecodeError, TypeError):
            return False
    
    def _should_use_async_task(self, query: str) -> bool:
        """Determine if query should use async task handling."""
        # For now, disable async tasks to ensure synchronous responses for the UI
        # This can be re-enabled when the UI supports polling for async task results
        return False
        
        # Original logic (disabled):
        # Simple queries that don't need async
        # simple_queries = ["hello", "help", "ping", "status", "health"]
        # query_lower = query.lower().strip()
        # 
        # if query_lower in simple_queries:
        #     return False
        # 
        # # Complex queries that need async
        # complex_indicators = [
        #     "search", "find", "analyze", "recommend", "generate",
        #     "complex", "detailed", "comprehensive", "thorough"
        # ]
        # 
        # return any(indicator in query_lower for indicator in complex_indicators)
    
    async def _start_async_task(self, query: str, context: RequestContext, event_queue: EventQueue) -> str:
        """Start async task for complex queries."""
        task_id = str(uuid.uuid4())
        
        if self.telemetry:
            with self.telemetry.get_a2a_telemetry().trace_task_execution(
                self.agent_name, task_id, "async_task"
            ) as span:
                span.set_attribute("query.text", query)
                span.set_attribute("task.id", task_id)
                
                # Start async processing
                self.active_tasks[task_id] = {
                    "query": query,
                    "start_time": time.time(),
                    "status": "running"
                }
                
                # Process in background
                asyncio.create_task(self._process_async_query(query, task_id, context))
                
                return f"Async task started with ID: {task_id}"
        else:
            # Fallback without telemetry
            self.active_tasks[task_id] = {
                "query": query,
                "start_time": time.time(),
                "status": "running"
            }
            asyncio.create_task(self._process_async_query(query, task_id, context))
            return f"Async task started with ID: {task_id}"
    
    async def _process_async_query(self, query: str, task_id: str, context: RequestContext):
        """Process async query."""
        try:
            if self.telemetry:
                with self.telemetry.get_a2a_telemetry().trace_task_execution(
                    self.agent_name, task_id, "async_processing"
                ) as span:
                    span.set_attribute("query.text", query)
                    span.set_attribute("task.id", task_id)
                    
                    # Execute the query
                    if self.smol_agent:
                        result = self.smol_agent.run(query)
                    else:
                        result = await self._handle_text_query(query)
                    
                    # Update task status
                    self.active_tasks[task_id]["status"] = "completed"
                    self.active_tasks[task_id]["result"] = result
                    self.active_tasks[task_id]["end_time"] = time.time()
                    
                    span.set_attribute("task.status", "completed")
                    span.set_attribute("result.length", len(str(result)))
                    
        except Exception as e:
            if self.telemetry:
                with self.telemetry.get_a2a_telemetry().trace_error(
                    self.agent_name, "async_task_error", str(e)
                ):
                    pass
            
            # Update task status
            self.active_tasks[task_id]["status"] = "error"
            self.active_tasks[task_id]["error"] = str(e)
            self.active_tasks[task_id]["end_time"] = time.time()
    
    async def _send_result(self, context: RequestContext, event_queue: EventQueue, result: Any):
        """Send result to event queue."""
        # Convert result to string if it's not already a string
        if not isinstance(result, str):
            if isinstance(result, (list, dict)):
                # Pretty print structured data
                import json
                result_str = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                # Convert other types to string
                result_str = str(result)
        else:
            result_str = result
        
        message = new_agent_text_message(result_str)
        await event_queue.enqueue_event(message)
    
    async def _send_error(self, context: RequestContext, event_queue: EventQueue, error: str):
        """Send error to event queue."""
        error_message = f"Error: {error}"
        message = new_agent_text_message(error_message)
        await event_queue.enqueue_event(message)
    
    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel execution with telemetry."""
        if self.telemetry:
            with self.telemetry.get_a2a_telemetry().create_span_with_context(
                "a2a.cancel",
                agent_name=self.agent_name
            ):
                logger.info(f"Cancelling execution for agent: {self.agent_name}")
        else:
            logger.info(f"Cancelling execution for agent: {self.agent_name}")
    
    async def query_other_agent(
        self,
        agent_name: str,
        query: Optional[str] = None,
        capability: Optional[str] = None,
        capability_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enhanced query other agent with telemetry."""
        if self.telemetry:
            with self.telemetry.get_a2a_telemetry().trace_agent_communication(
                self.agent_name, agent_name, "query"
            ) as span:
                try:
                    # Discover the agent
                    agents = await self.discovery_client.discover_agents_on_ports()
                    target_agent = None
                    
                    for agent in agents:
                        if agent.get('name') == agent_name:
                            target_agent = agent
                            break
                    
                    if not target_agent:
                        error_msg = f"Agent {agent_name} not found"
                        span.set_attribute("communication.status", "error")
                        span.set_attribute("communication.error", error_msg)
                        return {"error": error_msg}
                    
                    # Create connection
                    connection = AgentConnection(target_agent)
                    
                    # Send query
                    if query:
                        response = await connection.send_task(query)
                    elif capability:
                        response = await connection.invoke_capability(capability, capability_args or {})
                    else:
                        error_msg = "No query or capability specified"
                        span.set_attribute("communication.status", "error")
                        span.set_attribute("communication.error", error_msg)
                        return {"error": error_msg}
                    
                    # Record success
                    span.set_attribute("communication.status", "success")
                    span.set_attribute("response.length", len(str(response)))
                    
                    return response
                    
                except Exception as e:
                    span.set_attribute("communication.status", "error")
                    span.set_attribute("communication.error", str(e))
                    raise
        else:
            # Fallback without telemetry
            agents = await self.discovery_client.discover_agents_on_ports()
            target_agent = None
            
            for agent in agents:
                if agent.get('name') == agent_name:
                    target_agent = agent
                    break
            
            if not target_agent:
                return {"error": f"Agent {agent_name} not found"}
            
            connection = AgentConnection(target_agent)
            
            if query:
                return await connection.send_task(query)
            elif capability:
                return await connection.invoke_capability(capability, capability_args or {})
            else:
                return {"error": "No query or capability specified"}
    
    def _handle_get_agent_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get agent info capability."""
        return {
            "name": self.agent_name,
            "description": self.agent_description,
            "capabilities": list(self.capability_handlers.keys()),
            "telemetry_enabled": self.telemetry is not None
        }
    
    async def _handle_discover_agents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle discover agents capability."""
        try:
            agents = await self.discovery_client.discover_agents_on_ports()
            return {
                "agents": agents,
                "count": len(agents)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_query_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query agent capability."""
        agent_name = args.get("agent_name")
        query = args.get("query")
        
        if not agent_name or not query:
            return {"error": "agent_name and query are required"}
        
        return await self.query_other_agent(agent_name, query=query)
    
    @abstractmethod
    def setup_custom_capabilities(self):
        """Setup custom capabilities (to be implemented by subclasses)."""
        pass
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Get the agent card."""
        return self.agent_card
    
    def start_performance_monitoring(self):
        """Start performance monitoring for this agent."""
        if self.telemetry:
            self.telemetry.start_performance_monitoring(self.agent_name)
    
    def stop_performance_monitoring(self):
        """Stop performance monitoring for this agent."""
        if self.telemetry:
            self.telemetry.stop_performance_monitoring() 