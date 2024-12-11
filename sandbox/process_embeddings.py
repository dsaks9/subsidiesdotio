# process_embeddings.py

import pandas as pd
from openai import OpenAI
from pinecone.grpc import PineconeGRPC as Pinecone
import os
import time
import logging
import unicodedata
from dotenv import load_dotenv
from typing import List
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='process_embeddings.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logging.error("OpenAI API key not found. Please set OPENAI_API_KEY in the .env file.")
    print("Error: OpenAI API key not found. Please set OPENAI_API_KEY in the .env file.")
    exit(1)

OpenAI.api_key = OPENAI_API_KEY

# Pinecone API Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
if not PINECONE_API_KEY:
    logging.error("Pinecone API key not found. Please set PINECONE_API_KEY in the .env file.")
    print("Error: Pinecone API key not found. Please set PINECONE_API_KEY in the .env file.")
    exit(1)



def to_ascii(text: str) -> str:
    """
    Converts a string to its ASCII representation.
    
    Parameters:
    - text (str): The input text.
    
    Returns:
    - str: ASCII representation of the text.
    """
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def create_embedding(text: str) -> List[float]:
    client = OpenAI(api_key=OPENAI_API_KEY)
    """
    Creates an embedding for the given text using OpenAI's Ada-large model.
    
    Parameters:
    - text (str): The text to embed.
    
    Returns:
    - List[float]: The embedding vector.
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-3-large",  # Ensure this model is available and correct
            input=text,
            encoding_format="float"
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        logging.error(f"Error creating embedding for text: {text[:30]}... | Error: {e}")
        return []

def main():
    current_date = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_CSV = f'subsidies_final_with_embeddings{current_date}.csv'
    INPUT_CSV = r"C:\Users\caski\OneDrive\Documents\Gaido\Subsidies\DB scraping 2\venv\RVO subsidiewijzer\subsidies_final2024-12-02.csv"
    RATE_LIMIT_PER_MIN = 4000  # Adjust based on OpenAI's rate limits
    SECONDS_PER_REQUEST = 60 / RATE_LIMIT_PER_MIN  # Seconds to wait between requests
    PINECONE_INDEX = "subsidiewijzer-large-v3"

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX)

    # Clearing index
    try:
        index.delete(delete_all=True)
        logging.info(f"Deleted all entries from Pinecone index '{PINECONE_INDEX}'.")
        print(f"Deleted all entries from Pinecone index '{PINECONE_INDEX}'.")
    except Exception as e:
        logging.error(f"Failed to delete entries from Pinecone index '{PINECONE_INDEX}': {e}")
        print(f"Error: Failed to delete entries from Pinecone index '{PINECONE_INDEX}'. Check logs for details.")
        logging.error(f"Failed to delete entries from Pinecone index '{PINECONE_INDEX}': {e}")
        print(f"Error: Failed to delete entries from Pinecone index '{PINECONE_INDEX}'. Check logs for details.")


    # Check if input CSV exists
    if not os.path.isfile(INPUT_CSV):
        logging.error(f"Input CSV file '{INPUT_CSV}' not found.")
        print(f"Error: Input CSV file '{INPUT_CSV}' not found. Please ensure the file is in the current directory.")
        return

    # Read the final processed CSV
    try:
        df = pd.read_csv(INPUT_CSV)
        logging.info(f"Successfully read CSV file: {INPUT_CSV}")
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        print(f"Error: Failed to read CSV file. Check logs for details.")
        return

    # Check for 'summary' column
    if 'summary' not in df.columns:
        logging.error("'summary' column not found in the CSV.")
        print("Error: 'summary' column not found in the CSV.")
        return

    # Initialize the new column for embeddings
    df['vector_embedding'] = df['summary'].apply(lambda x: [])

    total_rows = len(df)
    logging.info(f"Starting embedding creation for {total_rows} rows.")
    print(f"Starting embedding creation for {total_rows} rows.")

    for index_row, row in df.iterrows():
        summary_text = row['summary']
        if pd.isnull(summary_text) or summary_text.strip() == "":
            logging.warning(f"Row {index_row + 1}: Summary is empty. Skipping embedding creation.")
            df.at[index_row, 'vector_embedding'] = []
            continue

        logging.info(f"Creating embedding for row {index_row + 1}/{total_rows}.")
        print(f"Creating embedding for row {index_row + 1}/{total_rows}.")

        embedding = create_embedding(summary_text)
        df.at[index_row, 'vector_embedding'] = embedding

        # Rate limiting
        time.sleep(SECONDS_PER_REQUEST)

    # Save the dataframe with embeddings
    try:
        df.to_csv(OUTPUT_CSV, index=False)
        logging.info(f"Successfully saved embeddings to '{OUTPUT_CSV}'.")
        print(f"Successfully saved embeddings to '{OUTPUT_CSV}'.")
    except Exception as e:
        logging.error(f"Failed to save the CSV with embeddings: {e}")
        print(f"Error: Failed to save the CSV with embeddings. Check logs for details.")
        return

    # Upsert embeddings into Pinecone
    logging.info(f"Starting upsert of embeddings into Pinecone index '{PINECONE_INDEX}'.")
    print(f"Starting upsert of embeddings into Pinecone index '{PINECONE_INDEX}'.")

    for idx, row in df.iterrows():
        embedding = row['vector_embedding']
        if not embedding:
            logging.warning(f"Row {idx + 1}: Embedding is empty. Skipping upsert.")
            continue

        vector_id = str(idx)  # Using DataFrame index as the ID

        # Prepare metadata
        metadata = {
            "text": row.get("summary", ""),
            "name": row.get("naam", ""),
            "aanvraagperiode": row.get("periode", ""),
            "url": row.get("url", ""),
            "status": row.get("status", ""),
            "category": row.get("categorie", ""),
            "max_budget": row.get("max_budget", ""),
            "max_subsidie": row.get("max_subsidie", ""),
            "aanmeldproces": row.get("aanmeldproces", "")
        }

        # Upsert the vector
        try:
            index.upsert(
                vectors=[
                    {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": metadata
                    }
                ]
            )
            logging.info(f"Upserted vector ID: {vector_id}")
        except Exception as e:
            logging.error(f"Failed to upsert vector ID: {vector_id} | Error: {e}")
            continue

        # Optional: Add a short sleep to respect Pinecone rate limits
        time.sleep(SECONDS_PER_REQUEST)

    logging.info("Completed upserting all embeddings into Pinecone.")
    print("Completed upserting all embeddings into Pinecone.")

if __name__ == "__main__":
    main()
