import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_urls_with_js(url):
    options = Options()
    options.headless = True  # Run Chrome in headless mode

    # Provide the path to your ChromeDriver executable
    driver_path = "/home/zhuoli/Projects/github/zhuoli/data/chromedriver"

    # Initialize Chrome WebDriver
    driver = webdriver.Chrome()

    # Navigate to the URL
    driver.get(url)

    # Optional: You could add some delay here to let the JavaScript content load, e.g.,
    # import time
    time.sleep(5)

    # Grab the page source
    page_source = driver.page_source

    driver.quit()
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract all links
    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]

    return links

if __name__ == "__main__":
    target_url = "https://docs.oracle.com/en-us/iaas/api/#/"  # Replace with the URL you want to scrape
    found_urls = extract_urls_with_js(target_url)
    
    print("Found URLs:")
    for url in found_urls:
        print(url)