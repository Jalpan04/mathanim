import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin

class ManimScraper:
    BASE_URL = "https://docs.manim.community/en/stable/reference.html"
    
    def __init__(self, output_dir="manim_docs"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def get_links(self):
        """Fetch all reference links from the main reference page."""
        response = requests.get(self.BASE_URL)
        if response.status_code != 200:
            print(f"Failed to load {self.BASE_URL}")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        # specific logic to find sidebar or main content links
        # This is a heuristic, might need adjustment based on actual page structure
        # Focusing on the API reference links usually found in toctrees
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'reference/manim.' in href and href.endswith('.html'):
                full_url = urljoin(self.BASE_URL, href)
                links.append(full_url)
        return list(set(links)) # Deduplicate

    def scrape_page(self, url):
        """Scrape content from a single page."""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main content
            content = soup.find('section') or soup.find('div', class_='document')
            if not content:
                return None
                
            # Clean up text
            text = content.get_text(separator='\n', strip=True)
            
            # Extract code examples
            code_blocks = []
            for pre in soup.find_all('pre'):
                code_blocks.append(pre.get_text())
                
            return {
                "url": url,
                "text": text,
                "code": code_blocks
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def run(self):
        print("Fetching links...")
        links = self.get_links()
        print(f"Found {len(links)} links. Starting scrape...")
        
        data = []
        for i, link in enumerate(links):
            print(f"Scraping [{i+1}/{len(links)}]: {link}")
            page_data = self.scrape_page(link)
            if page_data:
                data.append(page_data)
                
        output_file = os.path.join(self.output_dir, "manim_docs.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Scraping complete. Saved to {output_file}")

if __name__ == "__main__":
    scraper = ManimScraper()
    scraper.run()
