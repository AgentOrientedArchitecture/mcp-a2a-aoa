"""Tests for SMOL Telemetry Instrumentation."""

import pytest
import os
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from smol_instrumentation import SMOLTelemetryManager, DummySpanContext


class TestSMOLTelemetryManager:
    """Test cases for SMOLTelemetryManager."""
    
    def test_initialization(self):
        """Test SMOL telemetry manager initialization."""
        manager = SMOLTelemetryManager()
        assert manager.phoenix_endpoint == "http://localhost:6006/v1/traces"
        assert not manager.is_initialized()
    
    def test_initialization_with_custom_endpoint(self):
        """Test initialization with custom endpoint."""
        manager = SMOLTelemetryManager("http://custom:6006/v1/traces")
        assert manager.phoenix_endpoint == "http://custom:6006/v1/traces"
    
    def test_initialization_with_env_var(self):
        """Test initialization with environment variable."""
        os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://env:6006/v1/traces"
        manager = SMOLTelemetryManager()
        assert manager.phoenix_endpoint == "http://env:6006/v1/traces"
        del os.environ["PHOENIX_COLLECTOR_ENDPOINT"]
    
    @patch('smol_instrumentation.register')
    @patch('smol_instrumentation.SmolagentsInstrumentor')
    def test_setup_success(self, mock_instrumentor, mock_register):
        """Test successful setup."""
        mock_tracer_provider = Mock()
        mock_register.return_value = mock_tracer_provider
        
        manager = SMOLTelemetryManager()
        result = manager.setup("test-project")
        
        assert result == mock_tracer_provider
        assert manager.is_initialized()
        mock_register.assert_called_once()
        mock_instrumentor.return_value.instrument.assert_called_once()
    
    @patch('smol_instrumentation.register')
    def test_setup_failure(self, mock_register):
        """Test setup failure."""
        mock_register.side_effect = Exception("Setup failed")
        
        manager = SMOLTelemetryManager()
        
        with pytest.raises(Exception):
            manager.setup("test-project")
        
        assert not manager.is_initialized()
    
    def test_create_agent_span_not_initialized(self):
        """Test creating agent span when not initialized."""
        manager = SMOLTelemetryManager()
        span = manager.create_agent_span("test-agent", "test-operation")
        
        assert isinstance(span, DummySpanContext)
    
    @patch('smol_instrumentation.register')
    @patch('smol_instrumentation.SmolagentsInstrumentor')
    def test_create_agent_span_initialized(self, mock_instrumentor, mock_register):
        """Test creating agent span when initialized."""
        mock_tracer_provider = Mock()
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value = mock_span
        mock_register.return_value = mock_tracer_provider
        
        manager = SMOLTelemetryManager()
        manager.setup("test-project")
        
        # Mock the tracer
        with patch('smol_instrumentation.trace.get_tracer') as mock_get_tracer:
            mock_get_tracer.return_value = mock_tracer
            span = manager.create_agent_span("test-agent", "test-operation", custom_attr="value")
            
            assert span == mock_span
            mock_tracer.start_span.assert_called_once()
    
    def test_create_tool_call_span_not_initialized(self):
        """Test creating tool call span when not initialized."""
        manager = SMOLTelemetryManager()
        span = manager.create_tool_call_span("test-tool", "test-agent")
        
        assert isinstance(span, DummySpanContext)
    
    def test_create_llm_call_span_not_initialized(self):
        """Test creating LLM call span when not initialized."""
        manager = SMOLTelemetryManager()
        span = manager.create_llm_call_span("test-model", "test-agent")
        
        assert isinstance(span, DummySpanContext)
    
    def test_get_tracer_not_initialized(self):
        """Test getting tracer when not initialized."""
        manager = SMOLTelemetryManager()
        tracer = manager.get_tracer()
        
        assert tracer is None


class TestDummySpanContext:
    """Test cases for DummySpanContext."""
    
    def test_context_manager(self):
        """Test DummySpanContext as context manager."""
        span = DummySpanContext()
        
        with span as s:
            assert s == span
            s.set_attribute("test", "value")
            s.set_attributes({"test1": "value1", "test2": "value2"})
        
        # Should not raise any exceptions
        assert True 