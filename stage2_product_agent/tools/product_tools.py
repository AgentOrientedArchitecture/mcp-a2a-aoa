"""SMOL Agent Tools for Product Catalog - Stage 2 of Agent Oriented Architecture.

These tools add business intelligence and natural language understanding
on top of the basic MCP tools from Stage 1.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any

from smolagents import Tool

logger = logging.getLogger(__name__)


class FindSimilarProductsTool(Tool):
    """Find products similar to a given product based on category, price range, and rating."""
    
    name = "find_similar_products"
    description = "Find products similar to a given product based on category, price range, and rating"
    inputs = {
        "product_id": {
            "type": "integer",
            "description": "The ID of the reference product"
        },
        "max_results": {
            "type": "integer", 
            "description": "Maximum number of similar products to return (default: 5)",
            "nullable": True
        }
    }
    output_type = "string"
    
    def __init__(self, mcp_tools: Dict[str, Any]):
        """Initialize with MCP tools.
        
        Args:
            mcp_tools: Dictionary of MCP tools
        """
        super().__init__()
        self.mcp_tools = mcp_tools
    
    def forward(self, product_id: int, max_results: int = 5) -> str:
        """Find similar products.
        
        Args:
            product_id: The ID of the reference product
            max_results: Maximum number of similar products to return
            
        Returns:
            JSON string with similar products and similarity scores
        """
        try:
            # Get the reference product
            get_product = self.mcp_tools.get("get_product_by_id")
            if not get_product:
                return json.dumps({"error": "get_product_by_id tool not available"})

            ref_product_json = get_product(product_id=product_id)
            ref_product = json.loads(ref_product_json)

            if "error" in ref_product:
                return json.dumps({"error": f"Reference product not found: {ref_product['error']}"})

            # Search for similar products
            search_products = self.mcp_tools.get("search_products")
            if not search_products:
                return json.dumps({"error": "search_products tool not available"})

            # Search in the same category with similar price range
            price_margin = ref_product["price"] * 0.3  # 30% price margin
            similar_json = search_products(
                search_term=ref_product["category"],
                category=ref_product["category"],
                min_price=ref_product["price"] - price_margin,
                max_price=ref_product["price"] + price_margin
            )
            
            similar_data = json.loads(similar_json)
            if "error" in similar_data:
                return json.dumps({"error": f"Error searching similar products: {similar_data['error']}"})

            # Calculate similarity scores
            similar_products = []
            for product in similar_data.get("results", []):
                if product["id"] == product_id:
                    continue  # Skip the reference product

                # Simple similarity score based on price difference and rating
                price_diff = abs(product["price"] - ref_product["price"]) / ref_product["price"]
                rating_diff = abs(product["rating"] - ref_product["rating"]) / 5.0
                
                similarity_score = 1.0 - (price_diff * 0.6 + rating_diff * 0.4)
                
                similar_products.append({
                    "product": product,
                    "similarity_score": round(similarity_score, 2),
                    "price_difference": round(product["price"] - ref_product["price"], 2),
                    "rating_difference": round(product["rating"] - ref_product["rating"], 1)
                })

            # Sort by similarity score
            similar_products.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return json.dumps({
                "reference_product": ref_product,
                "similar_products": similar_products[:max_results],
                "total_found": len(similar_products)
            }, indent=2)

        except Exception as e:
            logger.error(f"Error finding similar products: {str(e)}")
            return json.dumps({"error": str(e)})


class AnalyzePriceTrendsTool(Tool):
    """Analyze price trends and statistics for products in a category."""
    
    name = "analyze_price_trends"
    description = "Analyze price trends and statistics for products in a category"
    inputs = {
        "category": {
            "type": "string",
            "description": "Product category to analyze (optional, analyzes all if not provided)",
            "nullable": True
        }
    }
    output_type = "string"
    
    def __init__(self, mcp_tools: Dict[str, Any]):
        """Initialize with MCP tools.
        
        Args:
            mcp_tools: Dictionary of MCP tools
        """
        super().__init__()
        self.mcp_tools = mcp_tools
    
    def forward(self, category: Optional[str] = None) -> str:
        """Analyze price trends.
        
        Args:
            category: Product category to analyze (optional)
            
        Returns:
            JSON string with price analysis including trends, outliers, and recommendations
        """
        try:
            # Get price range
            get_price_range = self.mcp_tools.get("get_price_range")
            if not get_price_range:
                return json.dumps({"error": "get_price_range tool not available"})

            price_range_json = get_price_range(category=category)
            price_range_data = json.loads(price_range_json)

            # Get all products in category for detailed analysis
            query_products = self.mcp_tools.get("query_products")
            if not query_products:
                return json.dumps({"error": "query_products tool not available"})

            if category:
                query = f"SELECT price, rating, stock_status FROM products WHERE category = '{category}' ORDER BY price"
            else:
                query = "SELECT price, rating, stock_status, category FROM products ORDER BY price"

            products_json = query_products(query=query)
            products_data = json.loads(products_json)

            if "error" in products_data:
                return json.dumps({"error": f"Error querying products: {products_data['error']}"})

            results = products_data.get("results", [])
            if not results:
                return json.dumps({"error": "No products found"})

            # Calculate statistics
            prices = [p["price"] for p in results]
            avg_price = sum(prices) / len(prices)
            
            # Find price quartiles
            sorted_prices = sorted(prices)
            q1_idx = len(sorted_prices) // 4
            q2_idx = len(sorted_prices) // 2
            q3_idx = 3 * len(sorted_prices) // 4
            
            q1 = sorted_prices[q1_idx]
            median = sorted_prices[q2_idx]
            q3 = sorted_prices[q3_idx]

            # Identify outliers (prices outside 1.5 * IQR)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = [p for p in prices if p < lower_bound or p > upper_bound]

            # Calculate stock status distribution
            stock_distribution = {}
            for product in results:
                status = product["stock_status"]
                stock_distribution[status] = stock_distribution.get(status, 0) + 1

            # Price-rating correlation
            rated_products = [(p["price"], p["rating"]) for p in results if p["rating"] > 0]
            avg_rating_by_price_tier = {
                "budget": [],
                "mid_range": [],
                "premium": []
            }
            
            if rated_products:
                for price, rating in rated_products:
                    if price <= q1:
                        avg_rating_by_price_tier["budget"].append(rating)
                    elif price <= q3:
                        avg_rating_by_price_tier["mid_range"].append(rating)
                    else:
                        avg_rating_by_price_tier["premium"].append(rating)
                
                for tier in avg_rating_by_price_tier:
                    ratings = avg_rating_by_price_tier[tier]
                    if ratings:
                        avg_rating_by_price_tier[tier] = round(sum(ratings) / len(ratings), 2)
                    else:
                        avg_rating_by_price_tier[tier] = None

            analysis = {
                "category": category or "all",
                "price_statistics": {
                    "min": price_range_data["price_range"]["min_price"],
                    "max": price_range_data["price_range"]["max_price"],
                    "average": round(avg_price, 2),
                    "median": round(median, 2),
                    "q1": round(q1, 2),
                    "q3": round(q3, 2),
                    "iqr": round(iqr, 2)
                },
                "outliers": {
                    "count": len(outliers),
                    "values": sorted(outliers)[:10]  # Show max 10 outliers
                },
                "stock_distribution": stock_distribution,
                "avg_rating_by_price_tier": avg_rating_by_price_tier if rated_products else None,
                "insights": []
            }

            # Generate insights
            if outliers:
                analysis["insights"].append(
                    f"Found {len(outliers)} price outliers that may need review"
                )
            
            if avg_price > median * 1.2:
                analysis["insights"].append(
                    "Average price is significantly higher than median, indicating premium products skew the average"
                )
            
            if stock_distribution.get("out_of_stock", 0) > len(results) * 0.2:
                analysis["insights"].append(
                    "Over 20% of products are out of stock - consider inventory management"
                )

            return json.dumps(analysis, indent=2)

        except Exception as e:
            logger.error(f"Error analyzing price trends: {str(e)}")
            return json.dumps({"error": str(e)})


class GenerateProductRecommendationsTool(Tool):
    """Generate personalized product recommendations based on customer preferences."""
    
    name = "generate_product_recommendations"
    description = "Generate personalized product recommendations based on customer preferences"
    inputs = {
        "customer_preferences": {
            "type": "object",
            "description": "Dictionary containing preferences like budget, categories, features"
        },
        "max_recommendations": {
            "type": "integer",
            "description": "Maximum number of recommendations to return (default: 5)",
            "nullable": True
        }
    }
    output_type = "string"
    
    def __init__(self, mcp_tools: Dict[str, Any]):
        """Initialize with MCP tools.
        
        Args:
            mcp_tools: Dictionary of MCP tools
        """
        super().__init__()
        self.mcp_tools = mcp_tools
    
    def forward(self, customer_preferences: Dict[str, any], max_recommendations: int = 5) -> str:
        """Generate recommendations.
        
        Args:
            customer_preferences: Dictionary containing preferences
            max_recommendations: Maximum number of recommendations
            
        Returns:
            JSON string with personalized product recommendations and reasoning
        """
        try:
            search_products = self.mcp_tools.get("search_products")
            if not search_products:
                return json.dumps({"error": "search_products tool not available"})

            # Extract preferences
            budget_max = customer_preferences.get("budget_max", None)
            budget_min = customer_preferences.get("budget_min", 0)
            preferred_categories = customer_preferences.get("categories", [])
            min_rating = customer_preferences.get("min_rating", 3.5)
            in_stock_only = customer_preferences.get("in_stock_only", True)
            search_keywords = customer_preferences.get("keywords", [])

            recommendations = []
            
            # Search based on preferences
            if preferred_categories:
                for category in preferred_categories:
                    # Search by category
                    results_json = search_products(
                        search_term=category,
                        category=category,
                        min_price=budget_min,
                        max_price=budget_max,
                        in_stock_only=in_stock_only
                    )
                    
                    results_data = json.loads(results_json)
                    if "results" in results_data:
                        for product in results_data["results"]:
                            if product["rating"] >= min_rating:
                                recommendations.append({
                                    "product": product,
                                    "match_reason": f"Matches preferred category: {category}",
                                    "score": product["rating"] / 5.0  # Simple scoring
                                })

            # Search by keywords if provided
            if search_keywords:
                for keyword in search_keywords:
                    results_json = search_products(
                        search_term=keyword,
                        min_price=budget_min,
                        max_price=budget_max,
                        in_stock_only=in_stock_only
                    )
                    
                    results_data = json.loads(results_json)
                    if "results" in results_data:
                        for product in results_data["results"]:
                            if product["rating"] >= min_rating:
                                # Check if already in recommendations
                                if not any(r["product"]["id"] == product["id"] for r in recommendations):
                                    recommendations.append({
                                        "product": product,
                                        "match_reason": f"Matches keyword: {keyword}",
                                        "score": product["rating"] / 5.0
                                    })

            # Sort by score and rating
            recommendations.sort(key=lambda x: (x["score"], x["product"]["rating"]), reverse=True)

            # Deduplicate and take top recommendations
            seen_ids = set()
            final_recommendations = []
            for rec in recommendations:
                if rec["product"]["id"] not in seen_ids:
                    seen_ids.add(rec["product"]["id"])
                    final_recommendations.append(rec)
                    if len(final_recommendations) >= max_recommendations:
                        break

            # Add recommendation reasons
            for rec in final_recommendations:
                product = rec["product"]
                reasons = [rec["match_reason"]]
                
                if product["rating"] >= 4.5:
                    reasons.append("Highly rated by customers")
                
                if budget_max and product["price"] <= budget_max * 0.7:
                    reasons.append("Great value within budget")
                
                if product["stock_status"] == "in_stock":
                    reasons.append("Available for immediate delivery")
                
                rec["reasons"] = reasons

            return json.dumps({
                "preferences_used": customer_preferences,
                "recommendations": final_recommendations,
                "total_matches": len(recommendations)
            }, indent=2)

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return json.dumps({"error": str(e)})


class NaturalLanguageProductSearchTool(Tool):
    """Convert natural language queries into structured product searches."""
    
    name = "natural_language_product_search"
    description = "Convert natural language queries into structured product searches"
    inputs = {
        "query": {
            "type": "string",
            "description": "Natural language search query"
        }
    }
    output_type = "string"
    
    def __init__(self, mcp_tools: Dict[str, Any]):
        """Initialize with MCP tools.
        
        Args:
            mcp_tools: Dictionary of MCP tools
        """
        super().__init__()
        self.mcp_tools = mcp_tools
    
    def forward(self, query: str) -> str:
        """Parse and execute natural language search.
        
        Args:
            query: Natural language search query
            
        Returns:
            JSON string with interpreted query and search results
        """
        try:
            search_products = self.mcp_tools.get("search_products")
            if not search_products:
                return json.dumps({"error": "search_products tool not available"})

            # Parse the natural language query
            query_lower = query.lower()
            
            # Extract price constraints
            min_price = None
            max_price = None
            if "under" in query_lower or "less than" in query_lower:
                # Extract price limit
                price_match = re.search(r'(?:under|less than)\s*\$?(\d+)', query_lower)
                if price_match:
                    max_price = float(price_match.group(1))
            
            if "above" in query_lower or "more than" in query_lower:
                price_match = re.search(r'(?:above|more than)\s*\$?(\d+)', query_lower)
                if price_match:
                    min_price = float(price_match.group(1))
            
            if "between" in query_lower:
                price_match = re.search(r'between\s*\$?(\d+)\s*and\s*\$?(\d+)', query_lower)
                if price_match:
                    min_price = float(price_match.group(1))
                    max_price = float(price_match.group(2))

            # Extract category hints
            categories = ["Electronics", "Books", "Clothing", "Home & Garden", "Sports"]
            detected_category = None
            for category in categories:
                if category.lower() in query_lower:
                    detected_category = category
                    break

            # Extract stock requirement
            in_stock_only = "in stock" in query_lower or "available" in query_lower

            # Extract search terms (remove price and stock phrases)
            search_terms = query_lower
            for phrase in ["under", "less than", "above", "more than", "between", "in stock", "available", "$"]:
                search_terms = search_terms.replace(phrase, " ")
            
            # Remove numbers and extra spaces
            search_terms = re.sub(r'\d+', '', search_terms)
            search_terms = ' '.join(search_terms.split())

            # Perform the search
            results_json = search_products(
                search_term=search_terms if search_terms else detected_category or "product",
                category=detected_category,
                min_price=min_price,
                max_price=max_price,
                in_stock_only=in_stock_only
            )

            results_data = json.loads(results_json)

            interpretation = {
                "original_query": query,
                "interpreted_as": {
                    "search_terms": search_terms,
                    "category": detected_category,
                    "price_range": {
                        "min": min_price,
                        "max": max_price
                    },
                    "in_stock_only": in_stock_only
                },
                "results": results_data
            }

            return json.dumps(interpretation, indent=2)

        except Exception as e:
            logger.error(f"Error in natural language search: {str(e)}")
            return json.dumps({"error": str(e)})