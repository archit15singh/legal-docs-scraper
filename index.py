from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import json
from loguru import logger

def scrape_page(page_url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Set the path to the Chrome binary and ChromeDriver based on the downloaded files
    chrome_binary_path = '/usr/bin/google-chrome-stable'
    chromedriver_path = '/workspaces/codespaces-blank/chromedriver'

    options.binary_location = chrome_binary_path
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)

    try:
        driver.get(page_url)
        time.sleep(5)  # Wait for the page to load (adjust as needed)

        page_source = driver.page_source
    except Exception as e:
        logger.error(f"Error fetching page {page_url}: {e}")
        return []  # Return an empty list if there's an error
    finally:
        driver.quit()  # Close the browser once the page is loaded

    soup = BeautifulSoup(page_source, 'html.parser')
    results = soup.find_all(class_='result')
    scraped_data = []

    for result in results:
        result_title = result.find('a', class_='result_title')
        result_title_href = result_title['href']
        result_title_text = result_title.get_text(strip=True)

        docsource = result.find(class_='docsource').get_text(strip=True)

        cites_tag = result.find('a', class_='cite_tag', href=True, text='Cites')
        cites_count = cites_tag.get_text(strip=True).split()[1]
        cites_href = cites_tag['href']

        cited_by_tag = result.find('a', class_='cite_tag', href=True, text='Cited by')
        cited_by_count = cited_by_tag.get_text(strip=True).split()[2]
        cited_by_href = cited_by_tag['href']

        data = {
            'result_title_href': result_title_href,
            'result_title_text': result_title_text,
            'datasource': docsource,
            'cites_count': cites_count,
            'cites_href': cites_href,
            'cited_by_count': cited_by_count,
            'cited_by_href': cited_by_href,
            'page_number': page_url[-1]
        }

        scraped_data.append(data)

    return scraped_data

if __name__ == "__main__":
    # Set up logging
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"{current_datetime}_run.log"
    logger.add(log_file, rotation="1 day")

    base_url = "https://indiankanoon.org/search/?formInput=doctypes%3A%20judgments%20fromdate%3A%201-1-1947%20todate%3A%2031-12-2023%20sortby%3A%20mostrecent&pagenum="

    final_result = []

    for pagenum in range(0, 40):  # 41 as the range is exclusive
        page_url = base_url + str(pagenum)
        logger.info(f"Scraping page {page_url}")
        scraped_data = scrape_page(page_url)
        final_result.extend(scraped_data)
        time.sleep(2)  # Add a sleep of 2 seconds between each page request
        break

    # Create a human-readable date and time string for the filename
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Save the final result to a JSON file with the human-readable date and time as the file name
    file_name = f"{current_datetime}.json"
    with open(file_name, "w") as outfile:
        json.dump(final_result, outfile, indent=4)

    logger.info(f"Data saved to {file_name}")
