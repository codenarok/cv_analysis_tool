import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Selectors based on README.md (might need adjustment)
JOB_LIST_CONTAINER_SELECTOR = 'ul[title="Job list"]' # Adjust if needed based on actual site structure
JOB_ITEM_SELECTOR = 'li.search-results-job-box' # Adjust if needed
JOB_LINK_SELECTOR = 'h3.search-results-job-box-title > a' # Adjust if needed
DEPARTMENT_SELECTOR = 'div.search-results-job-box-department' # Adjust if needed

def scrape_job_links_from_page(driver: WebDriver) -> list[dict]:
    """
    Scrapes job titles, links, and departments from the current job search results page.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        A list of dictionaries, where each dictionary contains 'title', 'link', and 'department'.
        Returns an empty list if scraping fails or no jobs are found.
    """
    job_links = []
    try:
        # Wait for the job list container to be present
        logging.info(f"Waiting for job list container: {JOB_LIST_CONTAINER_SELECTOR}")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, JOB_LIST_CONTAINER_SELECTOR))
        )
        logging.info("Job list container found.")

        # Find all job list items
        job_items = driver.find_elements(By.CSS_SELECTOR, JOB_ITEM_SELECTOR)
        logging.info(f"Found {len(job_items)} potential job items on the page.")

        if not job_items:
            logging.warning("No job items found on the current page.")
            return []

        for item in job_items:
            try:
                # Find the link element within the item
                link_element = item.find_element(By.CSS_SELECTOR, JOB_LINK_SELECTOR)
                job_title = link_element.text.strip()
                job_link = link_element.get_attribute('href')

                # Find the department element within the item
                try:
                    department_element = item.find_element(By.CSS_SELECTOR, DEPARTMENT_SELECTOR)
                    job_department = department_element.text.strip()
                except NoSuchElementException:
                    logging.warning(f"Department not found for job: {job_title}")
                    job_department = "Not specified"

                if job_title and job_link:
                    job_links.append({'title': job_title, 'link': job_link, 'department': job_department})
                else:
                    logging.warning("Found job item but could not extract title or link.")

            except NoSuchElementException:
                logging.warning(f"Could not find link element ({JOB_LINK_SELECTOR}) within a job item. Skipping item.")
            except Exception as e:
                logging.error(f"Error processing a job item: {e}")

        logging.info(f"Successfully extracted {len(job_links)} job links from the page.")
        return job_links

    except TimeoutException:
        logging.error(f"Timeout waiting for job list container ({JOB_LIST_CONTAINER_SELECTOR}).")
        return []
    except NoSuchElementException:
        logging.error(f"Could not find the main job list container ({JOB_LIST_CONTAINER_SELECTOR}).")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred during job list scraping: {e}")
        return []

if __name__ == '__main__':
    # Example Usage (requires a running WebDriver instance navigated to a sample page)
    # This example assumes you have initialized a driver and navigated to a
    # Civil Service Jobs search results page.
    # Import driver_setup relative to the script location if run directly
    import sys
    import os
    # Add src directory to path to allow importing driver_setup
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from scraping.driver_setup import initialize_driver

    driver = None
    try:
        # --- Setup for Example ---
        logging.info("Initializing driver for example...")
        driver = initialize_driver() # Use 'chrome' or 'firefox'

        # Navigate to the actual site (might require manual login first in a real scenario)
        target_url = "https://www.civilservicejobs.service.gov.uk/csr/index.cgi" # Example start page
        logging.info(f"Navigating to: {target_url}. Please perform a search manually if needed for testing.")
        driver.get(target_url)
        input("Please perform a job search on the website and press Enter here when the results page is loaded...")
        # --- End Setup ---

        logging.info("Attempting to scrape job links from the current page...")
        extracted_links = scrape_job_links_from_page(driver)

        if extracted_links:
            print("\n--- Extracted Job Links ---")
            for job in extracted_links:
                print(f"- Title: {job['title']}, Link: {job['link']}, Department: {job['department']}")
            print("--------------------------")
        else:
            print("\nNo job links were extracted.")

    except Exception as e:
        logging.error(f"An error occurred during the example run: {e}")
    finally:
        if driver:
            logging.info("Closing WebDriver for example...")
            driver.quit()
            logging.info("WebDriver closed.")
