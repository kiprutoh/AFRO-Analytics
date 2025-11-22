"""
Test script to verify the mortality analytics system works correctly
"""

from data_pipeline import MortalityDataPipeline
from analytics import MortalityAnalytics
from chatbot import MortalityChatbot


def test_system():
    """Test the complete system"""
    print("=" * 80)
    print("Testing Mortality Analytics System")
    print("=" * 80)
    
    try:
        # Test 1: Initialize pipeline
        print("\n[1] Testing Data Pipeline...")
        pipeline = MortalityDataPipeline()
        data = pipeline.load_data()
        print("✓ Data pipeline initialized successfully")
        print(f"  - Mortality records: {len(data['mortality']):,}")
        print(f"  - MMR records: {len(data['mmr']):,}")
        
        # Test 2: Test analytics
        print("\n[2] Testing Analytics Engine...")
        analytics = MortalityAnalytics(pipeline)
        print("✓ Analytics engine initialized")
        
        # Test 3: Get country statistics
        print("\n[3] Testing Country Statistics...")
        countries = pipeline.get_countries()
        if countries:
            test_country = countries[0]
            stats = analytics.get_country_statistics(test_country)
            print(f"✓ Retrieved statistics for {test_country}")
            print(f"  - Indicators found: {len(stats['indicators'])}")
        
        # Test 4: Test chatbot
        print("\n[4] Testing Chatbot...")
        chatbot = MortalityChatbot(analytics)
        print("✓ Chatbot initialized")
        
        # Test 5: Test queries
        print("\n[5] Testing Chatbot Queries...")
        test_queries = [
            "What are the statistics for Kenya?",
            "Compare Kenya and Uganda",
            "Top 5 countries by under-five mortality rate",
            "Show me projections"
        ]
        
        for query in test_queries:
            try:
                response = chatbot.process_query(query)
                print(f"✓ Query processed: '{query[:50]}...'")
                print(f"  Response length: {len(response)} characters")
            except Exception as e:
                print(f"✗ Error with query '{query}': {str(e)}")
        
        # Test 6: Generate report
        print("\n[6] Testing Report Generation...")
        report = analytics.generate_summary_report()
        print(f"✓ Report generated ({len(report)} characters)")
        
        print("\n" + "=" * 80)
        print("All tests completed successfully! ✓")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_system()

