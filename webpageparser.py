from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import time
from markdownify import markdownify as md

class WebPageParser:
    def __init__(self, base_url):
        self.visited_links = set()
        self.base_url = base_url
        self.driver = webdriver.Chrome()
        self.inc_count=0

    def parse(self, url):
        self.visited_links.add(url)
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        self.save_content(soup)
        links = self.extract_links(soup)
        for link in links:
            if link not in self.visited_links:
                time.sleep(1)
                self.parse(link)

    def save_content(self, soup):
        text = soup.get_text()
        lines = text.splitlines()
        cleaned_text = "\n".join(lines)

        # get file name
        words = cleaned_text.split()[:3]

        # Convert HTML to Markdown using markdownify
        markdown_text = md(str(soup.body))

        file_name_prefix = "_".join(words)
        file_name_prefix = re.sub(r"[^a-zA-Z0-9]+", "_", file_name_prefix)
        current_dir = os.getcwd()
        # Move up one level to the parent directory
        parent_dir = os.path.dirname(current_dir)
        # Set the path to the data folder
        data_folder = os.path.join(parent_dir, "data/langchain_doc")
        # Create the data folder if it doesn't exist
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        i=self.inc_count;
        self.inc_count+=1
        # Set the path to the output file
        output_file = os.path.join(data_folder, f"{i}_{file_name_prefix}.md")
        with open(output_file, "w") as f:
            f.write(markdown_text)

    def extract_links(self, soup):
        links = set([urljoin(self.base_url, a['href']) for a in soup.find_all('a', href=True)])
        return [link for link in links if link.startswith(self.base_url)]

    def close(self):
        self.driver.quit()
        
from datetime import datetime
import traceback

if __name__ == "__main__":
    ORACLE_DOCUMENT_URL = "https://docs.oracle.com/en-us/iaas/api" 

    print("Current date time: ", datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    parser = WebPageParser(ORACLE_DOCUMENT_URL)
    try:
        parser.parse(ORACLE_DOCUMENT_URL)
    except Exception as exc:
        print("Exception occurred: ", exc)
        print("Stacktrace: ")
        traceback.print_exc()
        print("Current date time: ", datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    parser.close()