from firecrawl import FirecrawlApp
import os
import json
from datetime import datetime
from urllib.parse import urljoin

def scrape_rvo_subsidies():
    # Initialize Firecrawl with API key
    app = FirecrawlApp()
    
    # URL to scrape
    base_url = 'https://www.rvo.nl/subsidies-financiering'
    
    try:
        print("Mapping RVO subsidies URLs...")
        
        # First, map all URLs on the page
        map_result = app.map_url(base_url)
        
        # Filter for subsidy URLs
        subsidy_urls = [url for url in map_result.get('links', []) 
                       if '/subsidies-financiering/' in url 
                       and url != base_url]
        
        print(f"Found {len(subsidy_urls)} subsidy URLs")
        
        # Create a directory for storing subsidy data
        os.makedirs('subsidies', exist_ok=True)
        
        # Store all results here
        all_subsidies = {
            'scrape_date': datetime.now().isoformat(),
            'base_url': base_url,
            'subsidies': []
        }
        
        # Scrape each subsidy page
        # for index, url in enumerate(subsidy_urls, 1):
        i = 1
        for url in subsidy_urls[0:5]:
            # print(f"Scraping subsidy {index}/{len(subsidy_urls)}: {url}")
            print(f'Scraping subsidy {i}/{len(subsidy_urls)}: {url}')
            
            try:
                # Scrape the individual page
                subsidy_result = app.scrape_url(
                    url,
                    params={
                        'formats': ['markdown', 'html'],
                        'onlyMainContent': True,
                        'waitFor': 5000,
                        'headers': {
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        }
                    }
                )
                
                subsidy_data = {
                    'url': url,
                    'scraped_date': datetime.now().isoformat(),
                    'title': subsidy_result.get('metadata', {}).get('title', ''),
                    'content': subsidy_result.get('markdown', ''),
                    'html': subsidy_result.get('html', ''),
                    'metadata': subsidy_result.get('metadata', {})
                }
                
                all_subsidies['subsidies'].append(subsidy_data)
                
                # Save individual subsidy data
                # filename = f"subsidies/subsidy_{index}.json"
                filename = f"subsidies/subsidy_{i}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(subsidy_data, f, ensure_ascii=False, indent=2)
                
                print(f"Saved subsidy data to {filename}")
                
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                continue
            
            i += 1
        
        # Save all results to a single file
        with open('all_subsidies.json', 'w', encoding='utf-8') as f:
            json.dump(all_subsidies, f, ensure_ascii=False, indent=2)
            
        print("\nAll processing completed!")
        print(f"Total subsidies processed: {len(all_subsidies['subsidies'])}")
        print("Results saved to all_subsidies.json and individual files in /subsidies directory")
        
    except Exception as e:
        print(f"Error occurred during processing: {str(e)}")
        raise

if __name__ == "__main__":
    scrape_rvo_subsidies() 