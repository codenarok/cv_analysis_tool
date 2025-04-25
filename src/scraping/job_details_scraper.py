import logging
import time
from datetime import date # Import date
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def safe_get_text(driver: WebDriver, by: By, value: str, attribute: str = None):
    """Safely finds an element and returns its text or attribute, handling NoSuchElementException."""
    try:
        element = driver.find_element(by, value)
        if attribute:
            return element.get_attribute(attribute)
        # Handle potential multiple lines/paragraphs within a field
        text_content = element.text.strip()
        # Replace multiple newlines/spaces with a single space for cleaner CSV output
        return ' '.join(text_content.split()) if text_content else None
    except NoSuchElementException:
        logging.warning(f"Element not found using {by}: {value}")
        return None # Return None if element not found

def scrape_job_details(driver: WebDriver, job_url: str, job_title: str, department: str) -> dict | None:
    """
    Navigates to a job details page and scrapes specified information using revised selectors.

    Args:
        driver: The Selenium WebDriver instance.
        job_url: The URL of the job details page.
        job_title: The title of the job (passed from the list page).
        department: The department of the job (passed from the list page).

    Returns:
        A dictionary containing the scraped job details, or None if navigation/critical scraping fails.
    """
    try:
        logging.info(f"Navigating to job details page: {job_url}")
        driver.get(job_url)
        # Wait for a key element in the main panel to ensure page is loaded
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'vac_display_panel_main_inner')]"))
        )
        logging.info("Job details page loaded.")
        # Add a small static delay just in case dynamic content needs more time
        time.sleep(1)
    except Exception as e:
        logging.error(f"Failed to navigate to or load {job_url}: {e}")
        return None

    # Get current date for Scrape Date
    scrape_date_str = date.today().strftime('%Y-%m-%d')

    # Initialize details dictionary with all expected fields (REVISED)
    details = {
        'Scrape Date': scrape_date_str, # Added
        'Job Title': job_title, # From list page
        'Reference Number': None,
        'Department': department, # From list page - Use the passed argument
        'Link': job_url, # From list page
        'Location': None,
        'Salary': None,
        'Job Grade': None,
        'Contract Type': None,
        'Role Type': None, # 'Type of Role' in selectors
        'Working Pattern': None,
        'Number Available': None, # New
        'Closing Date': None, # Added
        'Job Summary': None,
        'Job Description': None,
        'Person Specification': None,
        'Qualifications': None, # New
        'Behaviours': None, # New
        'Technical Skills': None, # New
        'Benefits': None,
        'Selection Process': None,
        'Contact Name': None,
        'Contact Email': None,
        'Match Score': None # Optional, remains None for now
    }

    logging.info("Scraping details from main panel...")
    # Main Panel Selectors (Using REVISED XPaths from README)
    details['Location'] = safe_get_text(driver, By.XPATH, "//h2[@id='section_link_location']/following-sibling::div[@class='vac_display_field'][1]//div[@class='vac_display_field_value']")
    details['Job Summary'] = safe_get_text(driver, By.XPATH, "//h3[normalize-space()='Job summary']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Job Description'] = safe_get_text(driver, By.XPATH, "//h3[normalize-space()='Job description']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Person Specification'] = safe_get_text(driver, By.XPATH, "//h3[normalize-space()='Person specification']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Qualifications'] = safe_get_text(driver, By.XPATH, "//h3[normalize-space()='Qualifications']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Behaviours'] = safe_get_text(driver, By.XPATH, "//h3[normalize-space()='Behaviours']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Technical Skills'] = safe_get_text(driver, By.XPATH, "//h3[normalize-space()='Technical skills']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Benefits'] = safe_get_text(driver, By.XPATH, "//h2[@id='section_link_benefits']/following-sibling::div[contains(@class, 'vac_display_field')]//div[contains(@class, 'vac_display_field_value')]")
    details['Selection Process'] = safe_get_text(driver, By.XPATH, "//h3[normalize-space()='Selection process details']/following-sibling::div//div[@class='vac_display_field_value']")
    details['Contact Name'] = safe_get_text(driver, By.XPATH, "//h4[normalize-space()='Job contact :']/following-sibling::ul[@class='contact_details']/li[span[normalize-space()='Name :']]/span[@class='contact_details_value']")
    details['Contact Email'] = safe_get_text(driver, By.XPATH, "//h4[normalize-space()='Job contact :']/following-sibling::ul[@class='contact_details']/li[span[normalize-space()='Email :']]/span[@class='contact_details_value']")

    # Scrape Closing Date using its specific class
    details['Closing Date'] = safe_get_text(driver, By.CSS_SELECTOR, ".vac_display_closing_date")

    logging.info("Scraping details from side panel...")
    # Side Panel Selectors (Using REVISED XPaths from README)
    side_panel_base = "//div[@class='vac_display_panel_side_inner']"
    details['Reference Number'] = safe_get_text(driver, By.XPATH, f"{side_panel_base}//h3[normalize-space()='Reference number']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Salary'] = safe_get_text(driver, By.XPATH, f"{side_panel_base}//h3[normalize-space()='Salary']/following-sibling::div[contains(@class,'vac_display_field_value')][1]")
    details['Job Grade'] = safe_get_text(driver, By.XPATH, f"{side_panel_base}//h3[normalize-space()='Job grade']/following-sibling::div//div[@class='vac_display_field_value'][1]")
    details['Contract Type'] = safe_get_text(driver, By.XPATH, f"{side_panel_base}//h3[normalize-space()='Contract type']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Role Type'] = safe_get_text(driver, By.XPATH, f"{side_panel_base}//h3[normalize-space()='Type of role']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Working Pattern'] = safe_get_text(driver, By.XPATH, f"{side_panel_base}//h3[normalize-space()='Working pattern']/following-sibling::div[@class='vac_display_field_value'][1]")
    details['Number Available'] = safe_get_text(driver, By.XPATH, f"{side_panel_base}//h3[normalize-space()='Number of jobs available']/following-sibling::div[@class='vac_display_field_value'][1]")

    # If Department wasn't found on list page OR was "Not specified", try side panel as fallback
    if not details['Department'] or details['Department'] == "Not specified":
        dept_fallback = safe_get_text(driver, By.XPATH, f"{side_panel_base}//h3[normalize-space()='Department']/following-sibling::div[@class='vac_display_field_value'][1]")
        if dept_fallback:
            details['Department'] = dept_fallback
            logging.info("Updated Department from details page side panel.")

    logging.info(f"Finished scraping details for: {job_title}")
    return details

# Example usage (requires a running WebDriver instance)
if __name__ == '__main__':
    # Add src directory to path to allow importing driver_setup
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) # Go up two levels
    from src.scraping.driver_setup import initialize_driver

    driver = None
    try:
        logging.info("Initializing driver for example...")
        driver = initialize_driver()

        # Example job (replace if needed)
        test_job_url = "https://www.civilservicejobs.service.gov.uk/csr/index.cgi?SID=cGFnZWFjdGlvbj12aWV3dmFjYnlqb2JsaXN0JnBhZ2VjbGFzcz1Kb2JzJnNlYXJjaHBhZ2U9MSZzZWFyY2hzb3J0PWNsb3Npbmcmb3duZXJ0eXBlPWZhaXImdXNlcnNlYXJjaGNvbnRleHQ9MTI5NjI2OTU2JmpvYmxpc3Rfdmlld192YWM9MTk0ODkwMSZvd25lcj01MDcwMDAwJnJlcXNpZz0xNzQ1NDQ3NDQ2LTc2ODE1ZWNjYmY1OTM1NTcwNjIzN2ExMmRmYTA0M2QwYzE2MDQ0YTI="
        test_job_title = "Associate Infrastructure Engineer - Super Computer Support" # Example title
        test_department = "Met Office" # Example department

        logging.info(f"Attempting to scrape details for: {test_job_url}")
        scraped_data = scrape_job_details(driver, test_job_url, test_job_title, test_department)

        if scraped_data:
            print("\n--- Scraped Job Details (Example) ---")
            for key, value in scraped_data.items():
                display_value = (str(value)[:100] + '...') if value and len(str(value)) > 100 else value
                print(f"- {key}: {display_value}")
            print("-------------------------------------")
        else:
            print("\nFailed to scrape job details for example.")

    except Exception as e:
        logging.error(f"An error occurred during the example run: {e}", exc_info=True)
    finally:
        if driver:
            logging.info("Closing WebDriver for example...")
            driver.quit()
            logging.info("WebDriver closed.")
