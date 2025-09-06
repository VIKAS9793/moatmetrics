"""
Test script for MoatMetrics Natural Language Analytics (TinyLlama-First)
Demonstrates the updated NLP query processing with hardware-aware model rotation
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from src.ai.memory_manager import AIMemoryManager
from src.ai.nl_analytics import NaturalLanguageAnalytics, AnalyticsContext


async def main():
    """Test the TinyLlama-first Natural Language Analytics service"""
    logger.info("🚀 Starting TinyLlama-First Natural Language Analytics test")
    
    try:
        # Initialize memory manager and analytics service
        memory_manager = AIMemoryManager()
        analytics = NaturalLanguageAnalytics(memory_manager)
        
        # Show system configuration
        logger.info("="*60)
        logger.info("SYSTEM CONFIGURATION")
        logger.info("="*60)
        
        system_info = analytics.get_system_info()
        for key, value in system_info.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")
        
        # Create sample MSP data context
        context = analytics.create_sample_context()
        
        # Test queries focusing on MSP business scenarios
        test_queries = [
            "Which clients generate the most revenue and which need immediate attention?",
            "How can we reduce software licensing costs while maintaining service quality?",
            "What's our current staff utilization rate and how can we optimize it?",
            "Give me a summary of our MSP business performance and key metrics",
            "What are the top 3 areas we should focus on to increase profitability?"
        ]
        
        logger.info("\n" + "="*60)
        logger.info("PROCESSING MSP BUSINESS QUERIES")
        logger.info("="*60)
        
        # Process each query individually
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n🔍 Query {i}/5: {query}")
            logger.info("-" * 60)
            
            result = await analytics.process_query(query, context, urgency="normal")
            
            print(f"\n💬 AI Response:")
            print(f"   {result.answer}")
            
            if result.insights and result.insights[0] != "Analysis completed based on available data":
                print(f"\n💡 Key Insights:")
                for insight in result.insights[:3]:  # Show top 3
                    print(f"   • {insight}")
            
            if result.recommendations and result.recommendations[0] != "Continue monitoring metrics for trends":
                print(f"\n📋 Action Items:")
                for rec in result.recommendations[:3]:  # Show top 3
                    print(f"   • {rec}")
            
            print(f"\n📊 Confidence: {result.confidence:.0%} | ⏱️  Time: {result.processing_time:.1f}s")
            
            # Small delay between queries
            await asyncio.sleep(2)
        
        # Test batch processing capability
        logger.info("\n" + "="*60)
        logger.info("TESTING BATCH PROCESSING")
        logger.info("="*60)
        
        batch_queries = [
            "What's our profit margin?",
            "Which licenses are underutilized?",
            "How many hours did staff work this month?",
            "What's our biggest cost center?",
            "Which client is most at risk of churn?"
        ]
        
        logger.info(f"Processing {len(batch_queries)} queries simultaneously...")
        
        batch_results = await analytics.batch_process_queries(batch_queries, context)
        
        for i, (query, result) in enumerate(zip(batch_queries, batch_results), 1):
            print(f"\n{i}. {query}")
            print(f"   Answer: {result.answer[:100]}..." if len(result.answer) > 100 else f"   Answer: {result.answer}")
            print(f"   Confidence: {result.confidence:.0%}")
        
        # Final system status
        logger.info("\n" + "="*60)
        logger.info("FINAL SYSTEM STATUS")
        logger.info("="*60)
        
        final_stats = memory_manager.get_memory_stats()
        logger.info(f"Models Loaded: {final_stats['loaded_models']}")
        logger.info(f"Total Queries Processed: {final_stats['total_model_usage']}")
        logger.info(f"Memory Used: {final_stats['ai_used_memory_gb']:.1f}GB / {final_stats['ai_max_memory_gb']:.1f}GB")
        logger.info(f"Hardware Tier: {final_stats['hardware_tier']}")
        
        logger.success("✅ TinyLlama-First Natural Language Analytics test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        raise
    finally:
        # Cleanup
        if 'memory_manager' in locals():
            await memory_manager.cleanup()


if __name__ == "__main__":
    # Run the test
    asyncio.run(main())
