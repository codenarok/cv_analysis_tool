# test_pagination.py
import logging
import time
import random
import os

# Import project modules
from src.config.config_loader import load_config
from src.scraping.driver_setup import initialize_driver
# No job scrapers needed for this test

# Selenium imports
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Set debug level for more detailed output during testing
logging.getLogger().setLevel(logging.DEBUG)


# --- Helper Function for Delay (copied from main.py) ---
def random_delay(min_seconds=3, max_seconds=6):
    """Waits for a random time between min_seconds and max_seconds."""
    delay = random.uniform(min_seconds, max_seconds)
    logging.info(f"Waiting for {delay:.2f} seconds...")
    time.sleep(delay)

# --- Test Execution ---
def test_next_button():
    """Tests finding and clicking the 'Next' button."""
    logging.info("Starting Pagination Test...")
    driver = None

    try:
        # 1. Load Configuration
        logging.info("Loading configuration...")
        config = load_config()
        logging.info("Configuration loaded.")

        # 2. Initialize WebDriver
        logging.info("Initializing WebDriver...")
        driver = initialize_driver(browser_name='chrome')
        logging.info("WebDriver initialized.")

        # 3. Navigate and Wait for Login/Search
        logging.info(f"Preparing to navigate to target URL: {config['TARGET_URL']}")
        random_delay(5, 8) # Shorter delay for testing
        driver.get(config['TARGET_URL'])
        logging.info("Navigation complete.")

        logging.info(f"Please log in (if required) and perform your desired job search on the website.")
        logging.info(f"Waiting for {config['LOGIN_WAIT_TIME']} seconds for manual setup...")
        print(f"\nACTION REQUIRED: Please log in and perform your job search in the browser window.")
        print(f"Waiting for {config['LOGIN_WAIT_TIME']} seconds before proceeding...")
        time.sleep(config['LOGIN_WAIT_TIME'])
        logging.info("Wait time finished. Attempting to find and click 'Next'.")

        current_search_page_url = driver.current_url
        logging.info(f"Current search results page URL: {current_search_page_url}")

        # 4. Find and Click Next Page Link (Logic copied from main.py)
        try:
            logging.info("Looking for pagination menu...")
            paging_menu_xpath = "//div[contains(@class, 'search-results-paging-menu')]"
            paging_menu = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, paging_menu_xpath))
            )
            logging.info("Pagination menu found.")

            # Log the HTML of the pagination menu for debugging
            try:
                paging_html = paging_menu.get_attribute('outerHTML')
                logging.debug(f"Pagination Menu HTML:\n{paging_html}") # Use debug level
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

            logging.info("Successfully initiated navigation to next page via JavaScript click.")
            # Add a wait after click to allow next page load initiation
            random_delay(5, 8)
            logging.info(f"Current URL after clicking 'Next': {driver.current_url}")
            if driver.current_url != current_search_page_url:
                 logging.info("SUCCESS: URL changed, likely navigated to the next page.")
            else:
                 logging.warning("WARNING: URL did not change after clicking 'Next'.")


        except TimeoutException:
            logging.error("TEST FAILED: No 'Next' page link found (or pagination menu timed out).")
        except NoSuchElementException:
             logging.error("TEST FAILED: No 'Next' page link element found within menu.")
        except Exception as e:
            logging.error(f"TEST FAILED: Error finding or clicking 'Next' page link: {e}", exc_info=True)

    except Exception as e:
        logging.error(f"An unexpected error occurred during the test setup: {e}", exc_info=True)
    finally:
        # 5. Close WebDriver
        if driver:
            logging.info("Closing WebDriver...")
            input("Press Enter in the terminal to close the browser...") # Keep browser open for inspection
            driver.quit()
            logging.info("WebDriver closed.")
        logging.info("Pagination Test finished.")

if __name__ == "__main__":
    test_next_button()
