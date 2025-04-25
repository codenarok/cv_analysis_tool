import docx
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_cv_text(file_path):
    """Reads and returns the text content from a .docx file."""
    if not file_path or not os.path.exists(file_path):
        logging.error(f"CV file path is invalid or file does not exist: {file_path}")
        raise FileNotFoundError(f"CV file not found at path: {file_path}")
    
    if not file_path.lower().endswith('.docx'):
        logging.error(f"Invalid file format. Expected .docx, got: {file_path}")
        raise ValueError("Invalid file format. Only .docx files are supported.")

    try:
        logging.info(f"Reading CV file: {file_path}")
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        cv_text = '\n'.join(full_text)
        logging.info(f"Successfully extracted text from CV. Length: {len(cv_text)} characters.")
        return cv_text
    except Exception as e:
        logging.error(f"Error reading .docx file {file_path}: {e}")
        raise

if __name__ == '__main__':
    # Example usage: Replace with a valid path to a .docx file for testing
    # Create a dummy .env file or set environment variable for testing
    # Example: Create a dummy_cv.docx file in the same directory
    # with open("dummy_cv.docx", "w") as f:
    #     f.write("This is a test CV document.") # Note: This creates an invalid docx, use Word to create a real one
    
    # Set env var for testing (or use a .env file)
    os.environ['CV_FILE_PATH_TEST'] = 'c:\\Users\\t-matasert\\source\\repos\\cv_analysis_tool\\tests\\fixtures\\dummy_cv.docx' # Adjust path as needed
    test_cv_path = os.getenv('CV_FILE_PATH_TEST')

    if test_cv_path and os.path.exists(test_cv_path):
        try:
            print(f"Testing CV reading with: {test_cv_path}")
            cv_content = read_cv_text(test_cv_path)
            print("\n--- CV Content Start ---")
            print(cv_content[:500] + "..." if len(cv_content) > 500 else cv_content) # Print first 500 chars
            print("--- CV Content End ---")
        except (FileNotFoundError, ValueError, Exception) as e:
            print(f"Error during test: {e}")
    else:
        print("Skipping example usage: Set the CV_FILE_PATH_TEST environment variable ")
        print("or create a dummy .env file with CV_FILE_PATH_TEST pointing to a valid .docx file.")
        # To run this test: 
        # 1. Create a dummy .docx file (e.g., using Microsoft Word).
        # 2. Set the environment variable CV_FILE_PATH_TEST to the full path of that file.
        #    Example (Windows CMD): set CV_FILE_PATH_TEST=C:\path\to\your\dummy_cv.docx
        #    Example (PowerShell): $env:CV_FILE_PATH_TEST="C:\path\to\your\dummy_cv.docx"
        #    Example (Bash/Zsh): export CV_FILE_PATH_TEST="/path/to/your/dummy_cv.docx"
        # 3. Run this script: python src/parsing/cv_parser.py
