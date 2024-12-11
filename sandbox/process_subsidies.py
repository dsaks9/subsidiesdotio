import pandas as pd
import requests
import json
import time
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='process_subsidies.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def web_to_markdown(url_to_scrape, api_key):
    """
    Sends a URL to the Firecrawl API and retrieves the markdown content.

    Parameters:
    - url_to_scrape (str): The URL to scrape.
    - api_key (str): Your Firecrawl API key.

    Returns:
    - str: The markdown content if successful, otherwise an error message.
    """
    firecrawl_api_url = "https://api.firecrawl.dev/v1/scrape"
    
    payload = {
        "url": url_to_scrape,
        "formats": ["markdown"],
        "onlyMainContent": True,
        "waitFor": 10,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(firecrawl_api_url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {}).get('markdown', "No markdown content found.")
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            logging.error(f"Failed to scrape URL: {url_to_scrape} | {error_msg}")
            return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"Request Exception: {e}"
        logging.error(f"Exception for URL: {url_to_scrape} | {error_msg}")
        return error_msg

def main():
    load_dotenv()
    # Constants
    current_date = datetime.now().strftime('%Y-%m-%d')
    print("hello world")
    CSV_FILENAME = r"C:\Users\caski\OneDrive\Documents\Gaido\Subsidies\DB scraping 2\venv\RVO subsidiewijzer\Data\extract-data-from-subsidie-en-financieringswijzer-rvo_rvo-subsidiewijzer_captured-list_2024-12-02_14-29-15_b7dac010-248c-4f16-9069-a43be07d4b4d.csv"
    OUTPUT_CSV = f'subsidies_processed_{current_date}.csv'
    if "utrecht" in CSV_FILENAME:
        loket = "utrecht"
        STATUS_FILTER = ["Aanvraagperiode open", "Aanvraagperiode nog niet open"]
    elif "subsidiewijzer" in CSV_FILENAME: 
        print("subsidiwijzer")
        STATUS_FILTER = ["Open voor aanvragen", "Bijna open voor aanvragen"]
        loket="subsidiewijzer"
    else:
        error_msg = "CSV filename does not contain 'wijzer' or 'utrecht'. Unable to determine STATUS_FILTER."
        logging.error(error_msg)
        print(f"Error: {error_msg}")
        return
    API_KEY = os.getenv('FIRECRAWL_API_KEY')  
    RATE_LIMIT_PER_MIN = 19
    SECONDS_PER_REQUEST = 60 / RATE_LIMIT_PER_MIN  # Approximately 3.16 seconds

    if not API_KEY:
        logging.error("Firecrawl API key not found. Please set FIRECRAWL_API_KEY in the .env file.")
        print("Error: Firecrawl API key not found. Please set FIRECRAWL_API_KEY in the .env file.")
        return

    # Check if CSV file exists
    if not os.path.isfile(CSV_FILENAME):
        logging.error(f"CSV file '{CSV_FILENAME}' not found.")
        print(f"Error: CSV file '{CSV_FILENAME}' not found. Please ensure the file is in the current directory.")
        return

    # Step 1: Import CSV as pandas dataframe
    try:
        df = pd.read_csv(CSV_FILENAME)
        logging.info(f"Successfully read CSV file: {CSV_FILENAME}")
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        print(f"Error: Failed to read CSV file. Check logs for details.")
        return

    # Step 2: Filter dataframe based on 'status' column
    if 'status' not in df.columns:
        logging.error("'status' column not found in the CSV.")
        print("Error: 'status' column not found in the CSV.")
        return

    filtered_df = df[df['status'].isin(STATUS_FILTER)].copy()
    filtered_df.reset_index(drop=True, inplace=True)
    logging.info(f"Filtered dataframe to {len(filtered_df)} rows based on status.")
    print(f"Filtered dataframe to {len(filtered_df)} rows based on status.")

    # Check if 'url' column exists
    if 'url' not in filtered_df.columns:
        logging.error("'url' column not found in the CSV.")
        print("Error: 'url' column not found in the CSV.")
        return

    # Initialize the new column with empty strings
    filtered_df['Markdown_content'] = ""

    total_urls = len(filtered_df)
    logging.info(f"Starting to process {total_urls} URLs.")
    print(f"Starting to process {total_urls} URLs.")

    for index, row in filtered_df.iterrows():
        url = row['url']
        logging.info(f"Processing URL {index + 1}/{total_urls}: {url}")
        print(f"Processing URL {index + 1}/{total_urls}: {url}")

        markdown_content = web_to_markdown(url, API_KEY)
        filtered_df.at[index, 'Markdown_content'] = markdown_content

        # Rate limiting
        if index < total_urls - 1:  # No need to sleep after the last request
            time.sleep(SECONDS_PER_REQUEST)

    # Step 4: Save the updated dataframe to a new CSV
    try:
        filtered_df.to_csv(OUTPUT_CSV, index=False)
        logging.info(f"Successfully saved the processed data to {OUTPUT_CSV}")
        print(f"Successfully saved the processed data to {OUTPUT_CSV}")
    except Exception as e:
        logging.error(f"Failed to save the processed CSV: {e}")
        print(f"Error: Failed to save the processed CSV. Check logs for details.")

if __name__ == "__main__":
    main()
