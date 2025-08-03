"""Tests for the Product Catalog Agent."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class TestProductCatalogAgent:
    """Test the Product Catalog Agent."""

    @patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "test-key",
        "MCP_SERVER_PATH": "stage1_mcp_product_server/server_fastmcp.py"
    })
    @patch('stage2_product_agent.agent.LiteLLMModel')
    @patch('stage2_product_agent.agent.Path')
    def test_agent_initialization(self, mock_path, mock_model):
        """Test agent initializes correctly."""
        from stage2_product_agent.agent import ProductCatalogAgent
        
        # Mock path exists
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.resolve.return_value = mock_path_instance
        mock_path.return_value = mock_path_instance
        
        # Initialize agent
        agent = ProductCatalogAgent()
        
        assert agent.agent_name == "ProductCatalogAssistant"
        assert mock_model.called

    @patch.dict(os.environ, {})
    def test_agent_no_api_key(self):
        """Test agent fails without API key."""
        from stage2_product_agent.agent import ProductCatalogAgent
        
        with pytest.raises(ValueError, match="No API key found"):
            ProductCatalogAgent()

    def test_get_customer_insights_empty_history(self):
        """Test customer insights with empty history."""
        from stage2_product_agent.agent import ProductCatalogAgent
        
        # Create agent instance without full initialization
        agent = ProductCatalogAgent.__new__(ProductCatalogAgent)
        
        insights = agent.get_customer_insights([])
        
        assert insights["categories"] == []
        assert insights["budget_min"] == 0
        assert insights["budget_max"] == 0
        assert insights["brand_preferences"] == []

    def test_get_customer_insights_with_history(self):
        """Test customer insights with purchase history."""
        from stage2_product_agent.agent import ProductCatalogAgent
        
        agent = ProductCatalogAgent.__new__(ProductCatalogAgent)
        
        history = [
            {"category": "Electronics", "price": 500, "brand": "TechCorp", "rating": 4.5},
            {"category": "Electronics", "price": 300, "brand": "TechCorp", "rating": 4.0},
            {"category": "Books", "price": 20, "brand": "Publisher A", "rating": 4.8},
        ]
        
        insights = agent.get_customer_insights(history)
        
        assert "Electronics" in insights["categories"]
        assert "TechCorp" in insights["brand_preferences"]
        assert insights["budget_min"] > 0
        assert insights["budget_max"] > 0
        assert insights["min_rating"] > 3.0