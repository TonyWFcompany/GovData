import requests
import json
from datetime import datetime, timedelta
import os
from time import sleep
from typing import List, Dict

class SAMGovScraper:
    def __init__(self, api_key: str):
        """
        Initialize the SAM.gov scraper with your API key.
        Get your API key from https://sam.gov/data-services/
        """
        self.api_key = api_key
        self.base_url = "https://api.sam.gov/opportunities/v2/search"
        self.headers = {
            "Content-Type": "application/json"
        }

    def search_opportunities(
        self,
        keywords: List[str],
        days_back: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search contract opportunities based on keywords.
        
        Args:
            keywords: List of keywords to search for
            days_back: How many days back to search
            limit: Maximum number of results to return
        
        Returns:
            List of matching opportunities
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Format dates for API in MM/dd/yyyy format
        date_format = "%m/%d/%Y"
        postedFrom = start_date.strftime(date_format)
        postedTo = end_date.strftime(date_format)

        # Prepare keyword query
        keyword_query = " OR ".join([f'"{k}"' for k in keywords])
        
        params = {
            "api_key": self.api_key,
            "limit": limit,
            "postedFrom": postedFrom,
            "postedTo": postedTo,
            "keywords": keyword_query
        }

        try:
            print(f"Making request to {self.base_url}")
            print(f"Parameters: {params}")
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code != 200:
                print(f"Error response: {response.text}")
            response.raise_for_status()
            
            data = response.json()
            
            if "opportunitiesData" not in data:
                print(f"Unexpected response format: {data}")
                return []
                
            return data["opportunitiesData"]
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching opportunities: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            return []

    def save_opportunities(
        self,
        opportunities: List[Dict],
        filename: str
    ) -> None:
        """
        Save opportunities to a JSON file.
        
        Args:
            opportunities: List of opportunities to save
            filename: Name of file to save to
        """
        # Create timestamp for the report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Add timestamp to filename
        filename_with_timestamp = f"{filename}_{timestamp}.json"
        
        # Save with pretty printing
        with open(filename_with_timestamp, 'w', encoding='utf-8') as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(opportunities)} opportunities to {filename_with_timestamp}")

    def filter_opportunities(
        self,
        opportunities: List[Dict],
        must_include_keywords: List[str]
    ) -> List[Dict]:
        """
        Filter opportunities to only include those with all specified keywords.
        
        Args:
            opportunities: List of opportunities to filter
            must_include_keywords: Keywords that must all be present
            
        Returns:
            Filtered list of opportunities
        """
        filtered = []
        
        for opp in opportunities:
            # Combine relevant text fields for searching
            searchable_text = " ".join([
                str(opp.get("title", "")),
                str(opp.get("description", "")),
                str(opp.get("type", "")),
                str(opp.get("classificationCode", ""))
            ]).lower()
            
            # Check if all keywords are present
            if all(keyword.lower() in searchable_text 
                  for keyword in must_include_keywords):
                filtered.append(opp)
                
        return filtered

    def print_summary(self, opportunities: List[Dict], title: str = "Opportunities"):
        """
        Print a summary of the opportunities.
        """
        print(f"\n{title} Summary:")
        print(f"Total count: {len(opportunities)}")
        
        for opp in opportunities:
            print("\n" + "-" * 80)
            print(f"Title: {opp.get('title')}")
            print(f"Notice ID: {opp.get('noticeId')}")
            print(f"Posted Date: {opp.get('postedDate')}")
            print(f"Response Due Date: {opp.get('responseDueDate')}")

def main():
    # ENTER YOUR API KEY HERE
    api_key = "zW917aZNkXKa08uDq8iC5InXrFXoGtDsLgJwWE9T"  # Your API key
    
    # Initialize scraper
    scraper = SAMGovScraper(api_key)
    
    # Define search parameters
    search_keywords = ["software", "development", "cloud"]  # Modify these keywords as needed
    must_include = ["python", "aws"]  # Must include ALL these keywords
    
    # Search for opportunities
    print("Searching for opportunities...")
    opportunities = scraper.search_opportunities(
        keywords=search_keywords,
        days_back=30,
        limit=100
    )
    
    # Save all results first
    scraper.save_opportunities(opportunities, "all_opportunities")
    
    # Filter results
    filtered_opportunities = scraper.filter_opportunities(
        opportunities,
        must_include_keywords=must_include
    )
    
    # Save filtered results
    scraper.save_opportunities(filtered_opportunities, "filtered_opportunities")
    
    # Print summaries
    scraper.print_summary(opportunities, "All Opportunities")
    scraper.print_summary(filtered_opportunities, "Filtered Opportunities")

if __name__ == "__main__":
    main()