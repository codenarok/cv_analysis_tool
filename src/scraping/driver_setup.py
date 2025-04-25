from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_driver(browser_name='chrome', headless=False):
    """Initializes and returns a Selenium WebDriver instance."""
    try:
        if browser_name.lower() == 'chrome':
            logging.info("Initializing Chrome WebDriver...")
            options = webdriver.ChromeOptions()
            # Add any desired options here (e.g., headless mode)
            if headless:
                logging.info("Headless mode enabled.")
                options.add_argument('--headless')
                options.add_argument('--disable-gpu') # Often needed for headless
                options.add_argument("--window-size=1920,1080") # Specify window size
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logging.info("Chrome WebDriver initialized successfully.")
        elif browser_name.lower() == 'firefox':
            logging.info("Initializing Firefox WebDriver...")
            options = webdriver.FirefoxOptions()
            # Add any desired options here
            if headless:
                logging.info("Headless mode enabled.")
                options.add_argument('--headless')
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            logging.info("Firefox WebDriver initialized successfully.")
        else:
            logging.error(f"Unsupported browser: {browser_name}")
            raise ValueError(f"Unsupported browser: {browser_name}. Please use 'chrome' or 'firefox'.")
        
        driver.implicitly_wait(10) # Default implicit wait
        return driver
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {e}")
        raise

if __name__ == '__main__':
    # Example usage: Initialize and quit the driver
    driver = None
    try:
        logging.info("Attempting to initialize WebDriver (Chrome, Headless)...")
        driver = initialize_driver(browser_name='chrome', headless=True)
        if driver:
            logging.info("WebDriver active. Navigating to example.com...")
            driver.get("https://example.com")
            logging.info(f"Page title: {driver.title}")
            logging.info("WebDriver test successful.")
        else:
             logging.error("Failed to initialize WebDriver.")
    except Exception as e:
        logging.error(f"An error occurred during WebDriver test: {e}")
    finally:
        if driver:
            logging.info("Closing WebDriver...")
            driver.quit()
            logging.info("WebDriver closed.")
