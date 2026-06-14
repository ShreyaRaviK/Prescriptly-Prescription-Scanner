import requests
from bs4 import BeautifulSoup
import json
import google.generativeai as genai

# Configuration
API_KEY = "AIzaSyD4OMf8IvXTAecxOB3QeUqYsLsofkDZmGk"
SEARCH_ENGINE_ID = "12c8a6cbb29db4a14"
GEMINI_API_KEY = "AIzaSyAJTKMVCl-SGu92abhNbU-Zriz6ZmAL0wY"

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def google_search(query):
    """Perform Google search using Custom Search JSON API"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 3
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Search failed: {e}")
        return None

def scrape_website_content(url):
    """Scrape text content from a webpage"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'meta']):
            element.decompose()
            
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"Scraping failed: {e}")
        return None

def main(name):
    """Main function that returns medication data as dictionary"""
    query = f"{name} 1mg"
    results = google_search(query)
    
    if not results or "items" not in results:
        return {"error": "No search results found"}

    first_result = None
    for item in results["items"]:
        if "1mg" in item["link"].lower():
            first_result = item
            break
    
    if not first_result:
        return {"error": "No relevant 1mg link found"}

    content = scrape_website_content(first_result["link"])
    
    if not content:
        return {"error": "Failed to scrape website content"}
    
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(f"""
        Extract structured data from the following content:
        {content}
        Provide the output in JSON format with these keys:
        {{
            "name": "Medicine Name",
            "price": "Price",
            "description": "Short description",
            "dosage": "Recommended dosage",
            "side_effects": "Possible side effects",
            "warnings": "Warnings"
        }}
    """)

    try:
        json_str = response.text.strip()
        json_start = json_str.find("{")
        json_end = json_str.rfind("}") + 1
        json_str = json_str[json_start:json_end]
        return json.loads(json_str)
    except json.JSONDecodeError:
        print("Error decoding JSON response")
        return {"error": "Could not process medication information"}

# For standalone testing
if __name__ == "__main__":
    input_name = "Amoxicillin 500mg Cap"
    result = main(input_name)
    print(json.dumps(result, indent=4))