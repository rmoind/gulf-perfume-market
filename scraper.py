import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys

# Target: Fetch real-time ratings to update database.

def scrape_perfume_real_time(url):
    """
    Scrapes rating from a live perfume page, bypassing 403 protections.
    """
    
    # STRATEGY 1: Add 'Referer', 'Accept', and 'Upgrade-Insecure-Requests' to look like a human coming from Google.
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1"
    }

    session = requests.Session()
    
    try:
        print(f" Connecting to: {url}...")
        response = session.get(url, headers=headers, timeout=15)
        
        # STRATEGY 2: Fallback to 'cloudscraper' if we still get 403
        if response.status_code == 403:
            print(" Standard request blocked (403). Attempting bypass with 'cloudscraper'...")
            try:
                import cloudscraper
                scraper = cloudscraper.create_scraper()
                response = scraper.get(url)
            except ImportError:
                print(" 'cloudscraper' library not found.")
                print(" Run 'pip install cloudscraper' to bypass Cloudflare protection.")
                return None

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract Data
            
            # 1. Rating
            # Fragrantica often uses microdata schemas
            rating = "N/A"
            rating_element = soup.find("span", itemprop="ratingValue")
            if rating_element:
                rating = rating_element.text.strip()
            
            # 2. Votes
            votes = "0"
            votes_element = soup.find("span", itemprop="ratingCount")
            if votes_element:
                votes = votes_element.text.strip()
            
            # 3. Name
            name = "Unknown"
            name_element = soup.find("h1", itemprop="name") # Standard schema
            if not name_element:
                name_element = soup.find("b", text=True) # Fallback for older pages
            if name_element:
                name = name_element.text.strip()

            print(" Data Extracted Successfully!")
            return {
                "name": name,
                "current_rating": rating,
                "total_votes": votes,
                "source_url": url,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f" Failed to retrieve page. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f" Error during scraping: {e}")
        return None

# --- Main Execution ---
if __name__ == "__main__":

    target_url = "https://www.fragrantica.com/perfume/Lattafa-Perfumes/Khamrah-75805.html"
    
    data = scrape_perfume_real_time(target_url)
    
    if data:
        print("\n--- SCRAPED RESULT ---")
        print(data)
        
        # Save to CSV
        df = pd.DataFrame([data])
        df.to_csv("scraped_live_update.csv", index=False)
        print(" Saved to scraped_live_update.csv")