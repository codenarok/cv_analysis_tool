import logging
import time
import random
import os

# Import project modules
from src.config.config_loader import load_config
from src.scraping.driver_setup import initialize_driver
from src.scraping.job_list_scraper import scrape_job_links_from_page
from src.scraping.job_details_scraper import scrape_job_details # Using the revised one
# from src.parsing.cv_parser import read_cv_text # Still commented out
# from src.ai.azure_analyzer import initialize_azure_client, analyze_text_with_azure # Still commented out
# from src.matching.matcher import compare_key_phrases # Still commented out
from src.data.csv_writer import save_to_csv

# Selenium imports for finding elements
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Function for Delay ---
def random_delay(min_seconds=10, max_seconds=15):
    """Waits for a random time between min_seconds and max_seconds."""
    delay = random.uniform(min_seconds, max_seconds)
    logging.info(f"Waiting for {delay:.2f} seconds...")
    time.sleep(delay)

# --- Main Execution ---
def main():
    """Main function: Scrapes job details across pages and saves to CSV."""
    logging.info("Starting CV Analysis Tool (Full Scraping & CSV Export Mode)...")
    driver = None
    all_job_details = [] # List to store details from all pages

    try:
        # 1. Load Configuration
        logging.info("Loading configuration...")
        config = load_config()
        logging.info("Configuration loaded.")

        # 2. Initialize WebDriver in Headless Mode
        logging.info("Initializing WebDriver in headless mode...")
        driver = initialize_driver(browser_name='chrome', headless=True) # Use headless mode
        logging.info("WebDriver initialized.")

        # 3. Navigate and Click Search
        logging.info(f"Navigating to target URL: {config['TARGET_URL']}")
        driver.get(config['TARGET_URL'])
        logging.info("Navigation complete.")
        random_delay(2, 4) # Short delay for page elements

        # Find and click the main search button
        search_button_id = "submitSearch"
        try:
            logging.info(f"Looking for search button with ID: {search_button_id}")
            search_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, search_button_id))
            )
            logging.info("Search button found and clickable.")
            # Use JavaScript click for potential robustness in headless mode
            driver.execute_script("arguments[0].click();", search_button)
            logging.info("Clicked the 'Search for jobs' button.")

            # Wait 30 seconds after clicking search for results to load
            wait_after_search = 30
            logging.info(f"Waiting {wait_after_search} seconds for search results to load...")
            time.sleep(wait_after_search)
            logging.info("Wait finished. Starting scraping process.")

        except TimeoutException:
            logging.error(f"Search button with ID '{search_button_id}' not found or not clickable within timeout. Exiting.")
            return # Exit if search button fails
        except Exception as e_search:
            logging.error(f"Error clicking search button: {e_search}", exc_info=True)
            return # Exit on other errors during search click

        page_number = 1
        while True: # Loop for pagination
            logging.info(f"--- Processing Page {page_number} ---")

            # Store the URL of the current search results page
            current_search_page_url = driver.current_url
            logging.info(f"Current search results page URL: {current_search_page_url}")

            # 4. Scrape Job List (Title, Link, Department) from Current Page
            logging.info("Scraping job list info from current page...")
            job_list_info = scrape_job_links_from_page(driver)

            if not job_list_info:
                logging.warning(f"No job links found on page {page_number}. Checking for 'Next' page.")
                # If no jobs found, still try to navigate back in case we are on a detail page somehow
                if driver.current_url != current_search_page_url:
                    logging.info(f"Navigating back to search results page: {current_search_page_url}")
                    driver.get(current_search_page_url)
                    random_delay(5, 8) # Wait for page to potentially reload
            else:
                logging.info(f"Found {len(job_list_info)} jobs on page {page_number}.")

                # 5. Process Each Job Link on the Current Page
                for i, job_info in enumerate(job_list_info):
                    job_url = job_info.get('link')
                    job_title = job_info.get('title', 'N/A')
                    job_department = job_info.get('department', 'N/A') # Get department

                    if not job_url:
                        logging.warning("Skipping job with missing link.")
                        continue

                    logging.info(f"\nProcessing job {i+1}/{len(job_list_info)}: '{job_title}' (Dept: {job_department})")

                    # Scrape details (pass title and department)
                    details = scrape_job_details(driver, job_url, job_title, job_department)

                    if details:
                        all_job_details.append(details)
                        logging.info(f"Successfully scraped details for '{job_title}'")
                    else:
                        logging.warning(f"Could not scrape details for job: {job_title} ({job_url})")

                # Navigate back ONCE after processing ALL jobs on the page
                logging.info(f"Finished processing all {len(job_list_info)} jobs on page {page_number}.")
                logging.info(f"Navigating back to search results page: {current_search_page_url}")
                driver.get(current_search_page_url)
                logging.info("Waiting for search results page to reload before checking for 'Next'...")
                random_delay(8, 12) # Wait for page to reload

            # 6. Find and Click Next Page Link (Now driver should be on the search results page)
            try:
                logging.info("Looking for pagination menu...")
                paging_menu_xpath = "//div[contains(@class, 'search-results-paging-menu')]"
                paging_menu = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, paging_menu_xpath))
                )
                logging.info("Pagination menu found.")

                # Log the HTML of the pagination menu for debugging (optional, can be removed later)
                try:
                    paging_html = paging_menu.get_attribute('outerHTML')
                    logging.debug(f"Pagination Menu HTML:\n{paging_html}")
                except Exception as e_html:
                    logging.warning(f"Could not get pagination menu HTML: {e_html}")

                logging.info("Looking for 'Next' page link within menu using title attribute...")
                # Use title attribute for potentially more robust selection
                next_link_xpath = ".//a[@title='Go to next search results page']" # Search within the menu element
                next_page_link = WebDriverWait(paging_menu, 20).until(
                    EC.presence_of_element_located((By.XPATH, next_link_xpath))
                )
                logging.info("Found 'Next' page link element using title.")

                # Add delay before clicking next page
                logging.info("Preparing to click 'Next' page link using JavaScript.")
                random_delay(3, 6) # Shorter delay before JS click

                logging.info("Attempting JavaScript click on 'Next' page link...")
                driver.execute_script("arguments[0].scrollIntoView(true);", next_page_link) # Scroll into view first
                time.sleep(0.5) # Brief pause after scroll
                driver.execute_script("arguments[0].click();", next_page_link)

                page_number += 1
                logging.info(f"Successfully initiated navigation to page {page_number} via JavaScript click.")
                # Add a wait after click to allow next page load initiation
                random_delay(5, 8)

            except TimeoutException:
                logging.info("No 'Next' page link found (or pagination menu timed out). Assuming end of results.")
                break # Exit the pagination loop
            except NoSuchElementException:
                 logging.info("No 'Next' page link element found within menu. Assuming end of results.")
                 break # Exit the pagination loop
            except Exception as e:
                logging.error(f"Error finding or clicking 'Next' page link: {e}", exc_info=True)
                logging.warning("Stopping pagination due to error.")
                break # Exit loop on error

        # 7. Save All Collected Data
        logging.info(f"\nFinished scraping all pages. Total jobs processed: {len(all_job_details)}")
        if all_job_details:
            output_filename = config['OUTPUT_CSV_FILE']
            absolute_output_path = os.path.abspath(output_filename)
            logging.info(f"Attempting to save all scraped job details to: {absolute_output_path}")
            save_to_csv(all_job_details, absolute_output_path)
        else:
            logging.info("No job details were successfully scraped.")

    except FileNotFoundError as e:
        logging.error(f"Configuration Error: {e}")
    except ValueError as e:
        logging.error(f"Configuration or Value Error: {e}")
    except ImportError as e:
        logging.error(f"Import Error: {e}. Make sure all dependencies are installed.")
    except Exception as e:
        logging.error(f"An unexpected error occurred in the main process: {e}", exc_info=True)
    finally:
        # 8. Close WebDriver
        if driver:
            logging.info("Closing WebDriver...")
            driver.quit()
            logging.info("WebDriver closed.")
        logging.info("CV Analysis Tool finished.")

if __name__ == "__main__":
    main()