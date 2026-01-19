#!/usr/bin/env python3
"""
Test script for NeurIPS scraper - tests multiple years and scenarios
"""

from neurips_scraper_prototype import NeurIPSScraper
import json


def test_multiple_years():
    """Test scraping from multiple NeurIPS years"""
    scraper = NeurIPSScraper()
    
    years_to_test = [2024, 2023, 2022]
    
    print("=" * 80)
    print("Testing NeurIPS Scraper across multiple years")
    print("=" * 80)
    
    all_results = {}
    
    for year in years_to_test:
        venue_id = f"NeurIPS.cc/{year}/Conference"
        print(f"\n\n{'='*80}")
        print(f"Testing {venue_id}")
        print(f"{'='*80}\n")
        
        papers = scraper.get_venue_submissions(venue_id, limit=3)
        
        if papers:
            print(f"[PASS] Successfully fetched {len(papers)} papers from NeurIPS {year}\n")
            
            for i, paper in enumerate(papers, 1):
                info = scraper.extract_paper_info(paper)
                print(f"{i}. {info['title']}")
                print(f"   Authors: {', '.join(info['authors'][:2])}{'...' if len(info['authors']) > 2 else ''}")
                print(f"   Keywords: {', '.join(info['keywords'][:3])}")
                print(f"   PDF: {info['pdf_url']}")
                print()
            
            all_results[year] = {
                'success': True,
                'count': len(papers),
                'sample_titles': [scraper.extract_paper_info(p)['title'] for p in papers]
            }
        else:
            print(f"[FAIL] No papers found for NeurIPS {year}")
            all_results[year] = {'success': False, 'count': 0}
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for year, result in all_results.items():
        status = "[PASS]" if result['success'] else "[FAIL]"
        print(f"NeurIPS {year}: {status} - Found {result['count']} papers")
    
    # Save results
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\nDetailed results saved to test_results.json")
    
    return all_results


def test_paper_details():
    """Test fetching detailed information for a specific paper"""
    scraper = NeurIPSScraper()
    
    print("\n\n" + "=" * 80)
    print("Testing detailed paper retrieval")
    print("=" * 80 + "\n")
    
    # Get a paper ID first
    venue_id = "NeurIPS.cc/2024/Conference"
    papers = scraper.get_venue_submissions(venue_id, limit=1)
    
    if papers:
        paper_id = papers[0]['id']
        print(f"Fetching details for paper ID: {paper_id}\n")
        
        details = scraper.get_paper_details(paper_id)
        if details:
            info = scraper.extract_paper_info(details)
            print(f"[PASS] Successfully retrieved paper details")
            print(f"\nTitle: {info['title']}")
            print(f"Authors: {len(info['authors'])} authors")
            print(f"Abstract length: {len(info['abstract'])} characters")
            print(f"Keywords: {', '.join(info['keywords'])}")
            print(f"Created: {info['created_time']}")
            print(f"Modified: {info['modified_time']}")
            return True
        else:
            print(f"[FAIL] Failed to retrieve paper details")
            return False
    else:
        print("[FAIL] Could not get initial paper to test")
        return False


if __name__ == "__main__":
    # Run tests
    results = test_multiple_years()
    detail_test = test_paper_details()
    
    # Overall status
    print("\n" + "=" * 80)
    print("OVERALL TEST STATUS")
    print("=" * 80)
    
    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"Year tests: {passed}/{total} passed")
    print(f"Detail test: {'PASS' if detail_test else 'FAIL'}")
    
    if passed == total and detail_test:
        print("\n[SUCCESS] All tests passed! Scraper is working correctly.")
    else:
        print("\n[FAILURE] Some tests failed. Check output above.")

