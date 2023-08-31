import traceback
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from queue import Queue
import sys

visited_links = set()  # A set to keep track of visited links to avoid infinite loops

def initialize_visited_links(link_file):
    try:
        with open(link_file, "r") as f:
            for line in f:
                visited_links.add(line.strip())
        print("Initialized succeed: added links number: " + str(len(visited_links)))
    except FileNotFoundError:
        print("page_links.txt not found, starting with an empty set.")

def extract_urls_with_js(page_link_file, base_url):
    url_queue = Queue()
    url_queue.put(base_url)

    while not url_queue.empty():
        current_url = url_queue.get()
        try:
            if current_url in visited_links:
                continue

            visited_links.add(current_url)

            # Initialize the WebDriver
            driver = webdriver.Chrome()

            # Navigate to the URL
            driver.get(current_url)

            # Grab the page source
            page_source = driver.page_source

            # Close the WebDriver
            driver.quit()

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract all links and convert them to absolute URLs
            all_links = set([urljoin(current_url, a['href']) for a in soup.find_all('a', href=True)])

            # Filter links to only include those that start with the base_url
            filtered_links = [link for link in all_links if link.startswith(base_url) and link not in visited_links]

            print(f"Visited: {current_url}, found {len(filtered_links)} links.")

            # Add each link to the queue to be visited
            for link in filtered_links:
                url_queue.put(link)

            # Write visited links to file
            write_links_to_file(filtered_links, page_link_file)
        except Exception as e:
            print("Error on parsing: " + current_url)
            print(f"An error occurred: {e}")
            traceback.print_exc()
            sys.exit(1)
            

def write_links_to_file(filtered_links,page_link_file):
    with open(page_link_file, "a") as f:
        for link in filtered_links:
            f.write(f"url : {link}\n")

ORACLE_DOCUMENT_URL = "https://docs.oracle.com/en-us/iaas/api" 

if __name__ == "__main__":
    base_url = ORACLE_DOCUMENT_URL
    page_link_file = "page_links.txt"
    initialize_visited_links(page_link_file)
    extract_urls_with_js(page_link_file,base_url)
    
    print("Found URLs:")
    for url in visited_links:
        print(url)