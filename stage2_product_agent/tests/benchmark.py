"""Benchmark Script for Stage 2 Agent Comparison.

This script runs predefined test queries through both SMOL and Agno agents
to provide a systematic comparison of their capabilities.
"""

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

# Add parent directory to path to import from stage1
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables only if not in Docker
if not os.getenv("DOCKER_CONTAINER", False):
    load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AgentBenchmark:
    """Benchmark tool for comparing SMOL and Agno agents."""

    def __init__(self):
        """Initialize the benchmark tool."""
        self.test_queries = self._get_test_queries()
        self.results = {
            "smol": {"success": 0, "errors": 0, "total_time": 0, "responses": []},
            "agno": {"success": 0, "errors": 0, "total_time": 0, "responses": []}
        }

    def _get_test_queries(self) -> List[Dict[str, str]]:
        """Get predefined test queries for benchmarking."""
        return [
            {
                "category": "Basic Search",
                "query": "Show me all laptops under $1000",
                "expected": "Should return laptops with prices under $1000"
            },
            {
                "category": "Complex Search",
                "query": "Find gaming laptops with at least 16GB RAM and SSD storage",
                "expected": "Should filter by gaming category, RAM, and storage type"
            },
            {
                "category": "Price Analysis",
                "query": "What's the average price of smartphones in our catalog?",
                "expected": "Should calculate and explain average smartphone price"
            },
            {
                "category": "Recommendations",
                "query": "I need a laptop for video editing, what do you recommend?",
                "expected": "Should provide personalized recommendations with reasoning"
            },
            {
                "category": "Data Analysis",
                "query": "Which product categories have the highest average price?",
                "expected": "Should analyze price trends across categories"
            },
            {
                "category": "Similar Products",
                "query": "Find products similar to the MacBook Pro",
                "expected": "Should identify similar laptops based on features"
            },
            {
                "category": "Business Intelligence",
                "query": "What are the top 5 most expensive products and why are they priced that way?",
                "expected": "Should analyze pricing strategy and provide insights"
            },
            {
                "category": "Natural Language",
                "query": "I'm looking for something to help me stay organized at work",
                "expected": "Should understand intent and suggest relevant products"
            },
            {
                "category": "Reasoning",
                "query": "If I have a budget of $500 and need both a laptop and a smartphone, what's the best combination?",
                "expected": "Should reason about budget allocation and optimal combinations"
            },
            {
                "category": "Explainability",
                "query": "Why would someone choose a tablet over a laptop?",
                "expected": "Should provide detailed reasoning about product choices"
            }
        ]

    def run_benchmark(self) -> Dict[str, Any]:
        """Run the full benchmark comparison."""
        print("=" * 80)
        print("Stage 2 Agent Framework Benchmark")
        print("Comparing SMOL vs Agno Agent Capabilities")
        print("=" * 80)
        print()
        
        # Initialize agents
        smol_agent = None
        agno_agent = None
        
        try:
            from agent import ProductCatalogAgent
            smol_agent = ProductCatalogAgent()
            print("✅ SMOL agent initialized")
        except Exception as e:
            print(f"❌ SMOL agent failed to initialize: {e}")
        
        try:
            from agno_agent import ProductCatalogAgnoAgent
            agno_agent = ProductCatalogAgnoAgent()
            print("✅ Agno agent initialized")
        except Exception as e:
            print(f"❌ Agno agent failed to initialize: {e}")
        
        if not smol_agent and not agno_agent:
            print("❌ No agents available for benchmarking")
            return {}
        
        print()
        print("Running benchmark tests...")
        print()
        
        # Run tests
        for i, test in enumerate(self.test_queries, 1):
            print(f"Test {i}/{len(self.test_queries)}: {test['category']}")
            print(f"Query: {test['query']}")
            print(f"Expected: {test['expected']}")
            print()
            
            # Test SMOL agent
            if smol_agent:
                start_time = time.time()
                try:
                    smol_response = smol_agent.run(test['query'])
                    end_time = time.time()
                    self.results["smol"]["success"] += 1
                    self.results["smol"]["total_time"] += (end_time - start_time)
                    self.results["smol"]["responses"].append({
                        "test": test,
                        "response": smol_response,
                        "time": end_time - start_time,
                        "status": "success"
                    })
                    print("🤖 SMOL: ✅ Success")
                except Exception as e:
                    self.results["smol"]["errors"] += 1
                    self.results["smol"]["responses"].append({
                        "test": test,
                        "response": str(e),
                        "time": 0,
                        "status": "error"
                    })
                    print(f"🤖 SMOL: ❌ Error - {e}")
            
            # Test Agno agent
            if agno_agent:
                start_time = time.time()
                try:
                    agno_response = agno_agent.query(test['query'])
                    end_time = time.time()
                    self.results["agno"]["success"] += 1
                    self.results["agno"]["total_time"] += (end_time - start_time)
                    self.results["agno"]["responses"].append({
                        "test": test,
                        "response": agno_response,
                        "time": end_time - start_time,
                        "status": "success"
                    })
                    print("🧠 Agno: ✅ Success")
                except Exception as e:
                    self.results["agno"]["errors"] += 1
                    self.results["agno"]["responses"].append({
                        "test": test,
                        "response": str(e),
                        "time": 0,
                        "status": "error"
                    })
                    print(f"🧠 Agno: ❌ Error - {e}")
            
            print("-" * 60)
            print()
        
        # Generate report
        self._generate_report()
        
        return self.results

    def _generate_report(self):
        """Generate a comprehensive benchmark report."""
        print("=" * 80)
        print("BENCHMARK REPORT")
        print("=" * 80)
        print()
        
        # Overall statistics
        print("📊 OVERALL STATISTICS")
        print("-" * 40)
        
        for agent, stats in self.results.items():
            total_tests = stats["success"] + stats["errors"]
            if total_tests > 0:
                success_rate = (stats["success"] / total_tests) * 100
                avg_time = stats["total_time"] / stats["success"] if stats["success"] > 0 else 0
                
                print(f"{agent.upper()}:")
                print(f"  Success Rate: {success_rate:.1f}% ({stats['success']}/{total_tests})")
                print(f"  Average Response Time: {avg_time:.2f}s")
                print(f"  Total Time: {stats['total_time']:.2f}s")
                print()
        
        # Detailed results by category
        print("📋 DETAILED RESULTS BY CATEGORY")
        print("-" * 40)
        
        categories = {}
        for agent, stats in self.results.items():
            for response in stats["responses"]:
                category = response["test"]["category"]
                if category not in categories:
                    categories[category] = {"smol": [], "agno": []}
                categories[category][agent].append(response)
        
        for category in categories:
            print(f"\n{category}:")
            for agent in ["smol", "agno"]:
                responses = categories[category].get(agent, [])
                if responses:
                    success_count = sum(1 for r in responses if r["status"] == "success")
                    avg_time = sum(r["time"] for r in responses if r["status"] == "success") / success_count if success_count > 0 else 0
                    print(f"  {agent.upper()}: {success_count}/{len(responses)} successful (avg: {avg_time:.2f}s)")
                else:
                    print(f"  {agent.upper()}: No tests run")
        
        # Recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        
        smol_stats = self.results.get("smol", {})
        agno_stats = self.results.get("agno", {})
        
        if smol_stats and agno_stats:
            smol_success = smol_stats["success"] / (smol_stats["success"] + smol_stats["errors"]) if (smol_stats["success"] + smol_stats["errors"]) > 0 else 0
            agno_success = agno_stats["success"] / (agno_stats["success"] + agno_stats["errors"]) if (agno_stats["success"] + agno_stats["errors"]) > 0 else 0
            
            smol_avg_time = smol_stats["total_time"] / smol_stats["success"] if smol_stats["success"] > 0 else float('inf')
            agno_avg_time = agno_stats["total_time"] / agno_stats["success"] if agno_stats["success"] > 0 else float('inf')
            
            print("Framework Comparison:")
            print(f"  SMOL Success Rate: {smol_success:.1%}")
            print(f"  Agno Success Rate: {agno_success:.1%}")
            print(f"  SMOL Avg Time: {smol_avg_time:.2f}s")
            print(f"  Agno Avg Time: {agno_avg_time:.2f}s")
            print()
            
            if smol_success > agno_success:
                print("🏆 SMOL shows better reliability")
            elif agno_success > smol_success:
                print("🏆 Agno shows better reliability")
            else:
                print("🤝 Both frameworks show similar reliability")
            
            if smol_avg_time < agno_avg_time:
                print("⚡ SMOL shows better performance")
            elif agno_avg_time < smol_avg_time:
                print("⚡ Agno shows better performance")
            else:
                print("⚡ Both frameworks show similar performance")
            
            print("\nRecommendation for Stage 3:")
            if agno_success >= smol_success and agno_avg_time <= smol_avg_time * 1.5:
                print("✅ Consider Agno for Stage 3 due to better reasoning capabilities")
            else:
                print("✅ Consider SMOL for Stage 3 due to better reliability/performance")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point for the benchmark script."""
    try:
        benchmark = AgentBenchmark()
        results = benchmark.run_benchmark()
        
        if not results:
            print("❌ No benchmark results generated")
            sys.exit(1)
        
        print("✅ Benchmark completed successfully!")
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 