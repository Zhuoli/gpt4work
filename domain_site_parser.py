import traceback
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from queue import Queue
import sys
import os
import re

class DomainSiteParser:
    def __init__(self,input_file):
        self.visited_links = set()  # A set to keep track of visited links to avoid infinite loops
        self.initialize_visited_links(input_file)

    def read_links_and_remove_duplicates(self, input_file, output_file):
        # Initialize visited_links set
        self.initialize_visited_links(input_file)

        # Convert set to list to write to file
        unique_links = list(self.visited_links)

        # Write unique links to output file
        with open(output_file, "w") as f:
            for link in unique_links:
                f.write(f"{link}\n")

        print(f"Removed duplicates and wrote to {output_file}")

    def initialize_visited_links(self, link_file):
        try:
            with open(link_file, "r") as f:
                for line in f:
                    # Extract the URL from the line
                    url = line.strip().split(" ")[-1]
                    if url.startswith('http'):
                        self.visited_links.add(url)
            print("Initialized succeed: added links number: " + str(len(self.visited_links)))
        except FileNotFoundError:
            print("page_links.txt not found, starting with an empty set.")

    def extract_urls_with_js(self,page_link_file, base_url):
        url_queue = Queue()
        url_queue.put(base_url)


        while not url_queue.empty():
            current_url = url_queue.get()
            try:
                if current_url in self.visited_links:
                    continue

                self.visited_links.add(current_url)

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
                filtered_links = [link for link in all_links if link.startswith(base_url) and link not in self.visited_links]

                print(f"Visited: {current_url}, found {len(filtered_links)} new links.")

                # Add each link to the queue to be visited
                for link in filtered_links:
                    url_queue.put(link)

                # Write visited links to file
                self.write_links_to_file(filtered_links, page_link_file)
            except Exception as e:
                print("Error on parsing: " + current_url)
                print(f"An error occurred: {e}")
                traceback.print_exc()
                sys.exit(1)
            

    def write_links_to_file(self, filtered_links,page_link_file):
        with open(page_link_file, "a") as f:
            for link in filtered_links:
                f.write(f"url : {link}\n")

    def save_content(self, link_list):
        # Initialize the WebDriver
        driver = webdriver.Chrome()

        for i, link in enumerate(link_list):
            # Navigate to the URL
            driver.get(link)

            # Grab the page source
            html_data = driver.page_source

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(html_data, "html.parser")
            text = soup.get_text()

            # Remove the first 835 lines
            lines = text.splitlines()
            cleaned_text = "\n".join(lines)

            # Get the first 3 words in the cleaned text
            words = cleaned_text.split()[:3]
            file_name_prefix = "_".join(words)

            # Replace special characters and spaces with an underscore
            file_name_prefix = re.sub(r"[^a-zA-Z0-9]+", "_", file_name_prefix)

            # Get the current working directory
            current_dir = os.getcwd()

            # Move up one level to the parent directory
            parent_dir = os.path.dirname(current_dir)

            # Set the path to the data folder
            data_folder = os.path.join(parent_dir, "data/langchain_doc")

            # Create the data folder if it doesn't exist
            if not os.path.exists(data_folder):
                os.makedirs(data_folder)

            # Set the path to the output file
            output_file = os.path.join(data_folder, f"{i}_{file_name_prefix}.txt")

            # Save the cleaned content to the output file
            with open(output_file, "w") as f:
                f.write(cleaned_text)

        # Close the WebDriver
        driver.quit()


ORACLE_DOCUMENT_URL = "https://docs.oracle.com/en-us/iaas/api" 

if __name__ == "__main__":
    base_url = ORACLE_DOCUMENT_URL
    page_link_file = "page_links.txt"

    parser = DomainSiteParser(page_link_file)
    parser.extract_urls_with_js(page_link_file,base_url)
    