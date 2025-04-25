import csv
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_to_csv(data: list[dict], filename: str):
    """Writes a list of dictionaries to a CSV file.

    Args:
        data: A list of dictionaries, where each dictionary represents a row.
              All dictionaries should ideally have the same keys.
        filename: The name (including path) of the CSV file to write.
    """
    if not data:
        logging.warning("No data provided to write to CSV.")
        return

    # Ensure the directory exists if filename includes a path
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")
        except OSError as e:
            logging.error(f"Error creating directory {directory}: {e}")
            return # Cannot proceed if directory creation fails

    try:
        # Use the keys from the first dictionary as header
        fieldnames = data[0].keys()
        
        logging.info(f"Writing {len(data)} rows to CSV file: {filename}")
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
            
        logging.info(f"Successfully wrote data to {filename}")

    except (IOError, csv.Error) as e:
        logging.error(f"Error writing to CSV file {filename}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during CSV writing: {e}")

if __name__ == '__main__':
    # Example Usage
    sample_data = [
        {'title': 'Job A', 'link': 'http://example.com/a', 'status': 'Open'},
        {'title': 'Job B', 'link': 'http://example.com/b', 'status': 'Closed'},
        {'title': 'Job C', 'link': 'http://example.com/c', 'status': 'Open'}
    ]
    output_file = 'test_output.csv'

    print(f"Attempting to write sample data to {output_file}...")
    save_to_csv(sample_data, output_file)

    # Verify file creation (optional)
    if os.path.exists(output_file):
        print(f"File '{output_file}' created successfully.")
        # Clean up the test file
        # os.remove(output_file)
        # print(f"Cleaned up {output_file}.")
    else:
        print(f"Failed to create file '{output_file}'.")
