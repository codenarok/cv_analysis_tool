# Civil Service Job Scraper and CV Matcher with Azure AI

## Project Goal

To create a Python application that automates the process of searching for jobs on the UK Civil Service Jobs website, scrapes relevant details from job postings (including closing dates), compares them against a user's CV using Azure AI Language service for suitability, and saves the matched job details along with the scrape date to a CSV file.

## Core Features

1.  **Automated Browser Navigation:** Uses Selenium to open the Civil Service Jobs website.
2.  **Manual Login:** Pauses execution to allow the user to log in manually.
3.  **Job List Scraping:** Extracts job titles, departments, and links from the search results page.
4.  **Detailed Job Scraping:** Navigates to each job link found and extracts detailed information (description, location, salary, grade, skills, closing date, etc.).
5.  **Date Recording:** Captures the date the script is run ('Scrape Date') for each job.
6.  **CV Processing:** Reads and processes text content from a user-provided CV file (`.docx`).
7.  **Azure AI Language Integration:** Uses Azure AI Language service (e.g., Key Phrase Extraction) to analyze both the CV and the scraped job descriptions.
8.  **CV Matching:** Compares the analysis results from the CV and job descriptions to determine job suitability based on defined criteria (e.g., keyword/phrase overlap).
9.  **Pagination Handling:** Automatically navigates through multiple pages of job search results.
10. **CSV Output:** Saves the details of *all* scraped jobs (including Scrape Date and Closing Date) to a CSV file.

## Prerequisites

*   Python 3.8+ installed.
*   Access to a web browser supported by Selenium (e.g., Chrome, Firefox).
*   An Azure account with an active subscription.
*   An Azure AI Language service resource created in the Azure portal.
*   The endpoint and an API key for the Azure AI Language resource.
*   A CV file in `.docx` format.

## Libraries to Install

```bash
pip install selenium webdriver-manager beautifulsoup4 lxml python-docx azure-ai-textanalytics python-dotenv
```

## Configuration

The application will require the following configuration, ideally stored securely (e.g., using a `.env` file and the `python-dotenv` library):

*   `TARGET_URL`: The starting URL for Civil Service Jobs (e.g., `https://www.civilservicejobs.service.gov.uk/csr/index.cgi`)
*   `CV_FILE_PATH`: The full path to the user's CV `.docx` file.
*   `AZURE_LANGUAGE_ENDPOINT`: The endpoint for your Azure AI Language resource.
*   `AZURE_LANGUAGE_KEY`: An API key for your Azure AI Language resource.
*   `OUTPUT_CSV_FILE`: The desired name for the output CSV file (e.g., `matched_jobs.csv`).
*   `LOGIN_WAIT_TIME`: Time in seconds to wait for manual login (e.g., 60).
*   `MATCH_THRESHOLD`: A value (e.g., number of overlapping key phrases) to determine if a job is suitable.

## Detailed Steps

1.  **Initialization:**
    *   Load configuration from environment variables (`.env` file).
    *   Initialize Selenium WebDriver using `webdriver-manager`.
    *   Initialize Azure `TextAnalyticsClient` using the endpoint and key.
    *   *(CSV header is now handled dynamically by `csv_writer.py`)*

2.  **Login and Navigate:**
    *   Navigate to `TARGET_URL`.
    *   Print a message asking the user to log in and perform a search.
    *   Wait for `LOGIN_WAIT_TIME` seconds (`time.sleep()`).

3.  **CV Processing (If Matching is Enabled - Currently Separate):**
    *   *(Steps for CV reading and analysis remain but are not integrated into the main scraping flow in `main.py` as currently written)*

4.  **Pagination Loop:**
    *   Start a loop that continues as long as there are jobs to process and potentially a "next" page.
    *   **Inside the loop:**
        *   **Scrape Job Links from Current Page (Scraping Point #1):**
            *   Wait for the job list container to be present.
            *   Find all job list items.
            *   For each list item, extract the job title, department, and the URL from the nested link.
            *   Store these as a list of dictionaries: `[{'title': '...', 'link': '...', 'department': '...'}, ...]`.
        *   **Process Each Job Link:**
            *   Create an empty list `all_job_details` to store data for *all* scraped jobs.
            *   Iterate through the extracted job links from the current page.
            *   For each job `job_info` (dictionary with title, link, department):
                *   Navigate to `job_info['link']`.
                *   **Scrape Job Details (Scraping Point #2):**
                    *   Wait for the main content panel to load.
                    *   Define a function `scrape_job_details(driver, job_url, job_title, department)`:
                        *   Get the current date (`Scrape Date`).
                        *   Initialize a dictionary `job_details` with all expected fields, including `Scrape Date`.
                        *   Use Selenium/BeautifulSoup to parse `driver.page_source`.
                        *   Extract data using specific selectors (see "HTML Element Selectors" below), including the `Closing Date`. Handle cases where elements might be missing. Store extracted details in the `job_details` dictionary.
                    *   Call `scrape_job_details` to get the `job_details` dictionary.
                    *   Append the `job_details` dictionary to the `all_job_details` list.
                *   *(Optional Delay):* Add a small `time.sleep()` between requests.
        *   **Navigate Back to Search Results:** After processing all jobs on the page, navigate back to the search results page URL.
        *   **Navigate to Next Page:**
            *   Attempt to find and click the "next" page link.
            *   If the link is found, increment page counter and continue loop.
            *   If the link is not found, break the pagination loop.

5.  **Save All Data:**
    *   After the loop finishes, check if `all_job_details` contains data.
    *   Define a function `save_to_csv(data_list, filename)`:
        *   Uses the `csv` module (`csv.DictWriter`).
        *   Opens the file in write mode (`'w'`) with `newline=''` and `encoding='utf-8'`.
        *   Dynamically gets `fieldnames` from the keys of the first dictionary in `data_list`.
        *   Writes the header row.
        *   Writes all rows from `data_list`.
    *   Call `save_to_csv` with `all_job_details` and the `OUTPUT_CSV_FILE` name.

6.  **Cleanup:**
    *   Close the browser: `driver.quit()`.
    *   Print "Scraping complete. Results saved to [CSV file name]."

## HTML Element Selectors (Examples)

Use Selenium's `find_element(s)` with `By.CSS_SELECTOR` or `By.XPATH`, or use BeautifulSoup's `select()` or `find()` methods.

**Job List Page:**

*   **Job List Container:** `ul[title="Job list"]`
*   **Individual Job Items:** `li.search-results-job-box`
*   **Job Title & Link (within item):** `h3.search-results-job-box-title > a` (get text and `href`)
*   **Department (within item):** `div.search-results-job-box-department` (get text)

**Job Details Page (Main Panel - `div.vac_display_panel_main`):**

*   **Closing Date:** `p.vac_display_closing_date` (CSS Selector)
*   **Location:** `#section_link_location + .vac_display_field .vac_display_field_value` (XPath: `//h2[@id='section_link_location']/following-sibling::div[@class='vac_display_field'][1]//div[@class='vac_display_field_value']`)
*   **Job Summary:** `h3:contains("Job summary") + .vac_display_field_value` (XPath: `//h3[normalize-space()='Job summary']/following-sibling::div[@class='vac_display_field_value'][1]`)
*   **Job Description:** `h3:contains("Job description") + .vac_display_field_value` (XPath: `//h3[normalize-space()='Job description']/following-sibling::div[@class='vac_display_field_value'][1]`)
*   **Person Specification/Skills:** `h3:contains("Person specification") + .vac_display_field_value` (XPath: `//h3[normalize-space()='Person specification']/following-sibling::div[@class='vac_display_field_value'][1]`)
*   **Qualifications:** (XPath: `//h3[normalize-space()='Qualifications']/following-sibling::div[@class='vac_display_field_value'][1]`)
*   **Behaviours:** (XPath: `//h3[normalize-space()='Behaviours']/following-sibling::div[@class='vac_display_field_value'][1]`)
*   **Technical Skills:** (XPath: `//h3[normalize-space()='Technical skills']/following-sibling::div[@class='vac_display_field_value'][1]`)
*   **Benefits:** `#section_link_benefits + .vac_display_field .vac_display_field_value` (XPath: `//h2[@id='section_link_benefits']/following-sibling::div[contains(@class, 'vac_display_field')]//div[contains(@class, 'vac_display_field_value')]`)
*   **Selection Process:** `h3:contains("Selection process details") + .vac_display_nullclass .vac_display_field_value` (XPath: `//h3[normalize-space()='Selection process details']/following-sibling::div//div[@class='vac_display_field_value']`)
*   **Contact Point Name:** `.contact_details_header:contains("Job contact") + .contact_details .contact_details_label:contains("Name") + .contact_details_value` (XPath: `//h4[normalize-space()='Job contact :']/following-sibling::ul[@class='contact_details']/li[span[normalize-space()='Name :']]/span[@class='contact_details_value']`)
*   **Contact Point Email:** `.contact_details_header:contains("Job contact") + .contact_details .contact_details_label:contains("Email") + .contact_details_value` (XPath: `//h4[normalize-space()='Job contact :']/following-sibling::ul[@class='contact_details']/li[span[normalize-space()='Email :']]/span[@class='contact_details_value']`)

**Job Details Page (Side Panel - `div.vac_display_panel_side_inner`):**

*   **Reference Number:** `//h3[text()='Reference number']/following-sibling::div[@class='vac_display_field_value']`
*   **Salary:** `//h3[text()='Salary']/following-sibling::div[@class='vac_display_field_value']` (might need to combine multiple divs)
*   **Job Grade:** `//h3[text()='Job grade']/following-sibling::div//div[@class='vac_display_field_value']`
*   **Contract Type:** `//h3[text()='Contract type']/following-sibling::div[@class='vac_display_field_value']`
*   **Type of Role:** `//h3[text()='Type of role']/following-sibling::div[@class='vac_display_field_value']`
*   **Working Pattern:** `//h3[text()='Working pattern']/following-sibling::div[@class='vac_display_field_value']`
*   **Number Available:** `//h3[text()='Number of jobs available']/following-sibling::div[@class='vac_display_field_value']` (XPath: `//h3[normalize-space()='Number of jobs available']/following-sibling::div[@class='vac_display_field_value'][1]`)
*   **Department (Fallback):** (XPath: `//h3[normalize-space()='Department']/following-sibling::div[@class='vac_display_field_value'][1]`)

*Note: These selectors are based on potential HTML structure and might need adjustments based on the actual website.*

## Data Structure (Example for CSV)

A dictionary for each scraped job, including fields like:

```python
{
    'Scrape Date': 'YYYY-MM-DD', # Added
    'Job Title': '...',
    'Reference Number': '...',
    'Link': '...',
    'Department': '...', # Scraped from list page or details page if possible
    'Location': '...',
    'Salary': '...',
    'Job Grade': '...',
    'Contract Type': '...',
    'Role Type': '...',
    'Working Pattern': '...',
    'Number Available': '...', # Renamed from 'Number of jobs available' for consistency
    'Closing Date': '...', # Added
    'Job Summary': '...',
    'Job Description': '...',
    'Person Specification': '...',
    'Qualifications': '...', # Added
    'Behaviours': '...', # Added
    'Technical Skills': '...', # Added
    'Benefits': '...',
    'Selection Process': '...',
    'Contact Name': '...',
    'Contact Email': '...',
    'Match Score': '...' # Optional: Store the score/reason for the match (if implemented)
}
```

The `fieldnames` for the `csv.DictWriter` will be dynamically generated from these keys by the `save_to_csv` function.

## Error Handling Considerations

*   Use `try-except` blocks for:
    *   File I/O (CV reading, CSV writing).
    *   Network requests (Selenium navigation, Azure API calls).
    *   Finding elements on the page (`NoSuchElementException`).
    *   Parsing HTML (`AttributeError` if structure is unexpected).
*   Implement retries for Azure API calls if appropriate (e.g., for transient network issues).
*   Log errors to a file or the console for debugging.
