"""
Test script for MoatMetrics Natural Language Analytics
Demonstrates the NLP query processing with sample MSP data
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from src.ai.memory_manager import AIMemoryManager
from src.ai.nl_analytics import NaturalLanguageAnalytics, AnalyticsContext


async def main():
    """Test the Natural Language Analytics service"""
    logger.info("Starting Natural Language Analytics test")
    
    try:
        # Initialize memory manager and analytics service
        memory_manager = AIMemoryManager()
        
        analytics = NaturalLanguageAnalytics(memory_manager)
        
        # Create sample MSP data context
        context = analytics.create_sample_context()
        
        # Test queries for different MSP scenarios
        test_queries = [
            "Which clients are the most profitable and which ones need attention?",
            "How can we improve our software license utilization to reduce costs?", 
            "What's our team productivity and how can we optimize staff resources?",
            "Give me an overall summary of our business performance this month",
            "What are the main areas we should focus on to increase profitability?"
        ]
        
        logger.info("Processing test queries...")
        
        # Process each query individually
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Query {i}: {query}")
            logger.info(f"{'='*60}")
            
            result = await analytics.process_query(query, context, urgency="normal")
            
            print(f"\n🤖 Answer: {result.answer}")
            print(f"\n💡 Key Insights:")
            for insight in result.insights:
                print(f"   • {insight}")
            
            print(f"\n📋 Recommendations:")
            for rec in result.recommendations:
                print(f"   • {rec}")
            
            print(f"\n📊 Confidence: {result.confidence:.2f}")
            print(f"⏱️  Processing Time: {result.processing_time:.2f}s")
            print(f"📂 Data Sources: {', '.join(result.data_sources)}")
            
            # Small delay between queries
            await asyncio.sleep(1)
        
        # Test batch processing
        logger.info(f"\n{'='*60}")
        logger.info("Testing batch query processing...")
        logger.info(f"{'='*60}")
        
        batch_queries = [
            "What's our current profit margin?",
            "Which licenses are underutilized?",
            "How many staff hours were logged this month?"
        ]
        
        batch_results = await analytics.batch_process_queries(batch_queries, context)
        
        for i, (query, result) in enumerate(zip(batch_queries, batch_results), 1):
            print(f"\nBatch Query {i}: {query}")
            print(f"Answer: {result.answer}")
            print(f"Confidence: {result.confidence:.2f}")
        
        logger.success("Natural Language Analytics test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise
    finally:
        # Cleanup
        if 'memory_manager' in locals():
            await memory_manager.cleanup()


if __name__ == "__main__":
    # Run the test
    asyncio.run(main())
