import json
from pathlib import Path
import sys
from llama_index.core import Document
from pydantic import BaseModel, ValidationError
from openai import OpenAI
from enum import Enum
import os
import time
import pickle
from datetime import datetime

from llama_index.core import Settings, Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core.node_parser import SentenceSplitter

from qdrant_client import QdrantClient

from agent.tools.tool_query_subsidies import CategorieSelectie

from agent.prompts.prompts import SYSTEM_PROMPT_CATEGORY_EXTRACTOR

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OpenAI.api_key = OPENAI_API_KEY

client_openai = OpenAI()


def load_subsidy_data(file_paths: list[str]) -> list:
    """
    Load and combine subsidy data from multiple JSON files.
    
    Args:
        file_paths (list[str]): List of paths to JSON files containing subsidy data
        
    Returns:
        list: Combined list of subsidy dictionaries
    """
    all_data = []
    for file_path in file_paths:
        print(f"\nAttempting to load data from: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Successfully loaded {len(data)} items from {file_path}")
            all_data.extend(data)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file {file_path}")
    
    print(f"Total items loaded: {len(all_data)}")
    return all_data

def extract_region(summary: str) -> str:
    """
    Extract the region from the summary of a subsidy.
    """
    class Regions(Enum):
        Drenthe = "Drenthe"
        Flevoland = "Flevoland"
        Friesland = "Friesland"
        Gelderland = "Gelderland"
        Groningen = "Groningen"
        Limburg = "Limburg"
        Noord_Brabant = "Noord-Brabant"
        Noord_Holland = "Noord-Holland"
        Overijssel = "Overijssel"
        Utrecht = "Utrecht"
        Zeeland = "Zeeland"
        Zuid_Holland = "Zuid-Holland"

    class Region(BaseModel):
        region: list[Regions]

    completion = client_openai.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Haal de regio uit de samenvatting."},
        {"role": "user", "content": summary},
    ],
    response_format=Region,
    )

    region = completion.choices[0].message.parsed

    region = [region.value for region in region.region]

    return region

def extract_category(summary: str) -> dict:
    """
    Extract the category from the summary of a subsidy.
    """

    system_prompt = SYSTEM_PROMPT_CATEGORY_EXTRACTOR
    completion = client_openai.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": summary},
    ],
    response_format=CategorieSelectie,
    )

    categories = completion.choices[0].message.parsed

    categories = categories.model_dump()

    return categories

def convert_none_to_false(d):
    """Recursively convert None values to False in a dictionary"""
    if isinstance(d, dict):
        return {k: convert_none_to_false(v) if isinstance(v, dict) else False if v is None else v 
               for k, v in d.items()}
    return d

def fill_missing_categories(output_dict, schema, original_schema=None):
    """
    Recursively fill in missing categories and subcategories with False based on the Pydantic schema.
    
    Args:
        output_dict (dict): The current dictionary with some values filled in
        schema (dict): The current level schema
        original_schema (dict): The complete original schema with $defs (used for recursion)
    
    Returns:
        dict: A complete dictionary with all categories and subcategories filled in
    """
    result = {}
    
    # On first call, set original_schema
    if original_schema is None:
        original_schema = schema
    
    # Get the properties from the schema
    properties = schema.get('properties', {})
    
    # Go through each property in the schema
    for prop_name, prop_schema in properties.items():
        current_value = output_dict.get(prop_name)
        
        # Handle anyOf cases
        if 'anyOf' in prop_schema:
            # Check if it's a reference to another schema
            ref_schema = next((t.get('$ref') for t in prop_schema['anyOf'] if '$ref' in t), None)
            
            if ref_schema:
                # Get the referenced schema name
                ref_name = ref_schema.split('/')[-1]
                # Get the full referenced schema
                full_ref_schema = original_schema['$defs'][ref_name]
                
                # Recursively fill in the nested object
                if isinstance(current_value, dict):
                    result[prop_name] = fill_missing_categories(current_value, full_ref_schema, original_schema)
                elif current_value is False or current_value is None:
                    # If the current value is False or None, create a new dict with all False values
                    result[prop_name] = fill_missing_categories({}, full_ref_schema, original_schema)
                else:
                    result[prop_name] = current_value
            else:
                # If it's a simple boolean/null property
                result[prop_name] = False if current_value is None else current_value
        else:
            # For any other case, keep the existing value or set to False
            result[prop_name] = False if current_value is None else current_value
            
    return result

def create_documents_from_subsidies(subsidies: list) -> list[Document]:
    """Create llama_index Documents from subsidy data."""
    print(f"\nAttempting to create documents from {len(subsidies)} subsidies")
    documents = []
    for i, subsidy in enumerate(subsidies):
        try:
            print(f"\nProcessing subsidy {i + 1}/{len(subsidies)}")
            print(f"Title: {subsidy.get('title', 'No title')}")

            bereik = subsidy.get('Bereik', '')
            if bereik == 'Regional':
                bereik = extract_region(subsidy.get('Samenvatting', ''))
            else:
                bereik = ["National"]

            # Extract categories and convert None to False
            categories = extract_category(subsidy.get('Samenvatting', ''))
            categories_converted = convert_none_to_false(categories)

            schema = CategorieSelectie.model_json_schema()
            categories_filled = fill_missing_categories(categories_converted, schema)

            # Create metadata dictionary with all fields including categories
            metadata = {
                'title': subsidy.get('title', ''),
                'Afkorting': subsidy.get('Afkorting', ''),
                'Laatste wijziging': subsidy.get('Laatste wijziging', ''),
                "Status": subsidy.get('Status', ''),
                "Deadline": subsidy.get('Deadline', ''),
                "Minimale bijdrage": subsidy.get('Minimale bijdrage', ''),
                "Maximale bijdrage": subsidy.get('Maximale bijdrage', ''),
                "Budget": subsidy.get('Budget', ''),
                "Aanvraagtermijn": subsidy.get('Aanvraagtermijn', ''),
                "Bereik": bereik,
                "Indienprocedure": subsidy.get('Indienprocedure', ''),
                "Categories": categories_filled,  # Add the categories to metadata
            }

            document = Document(
                text=subsidy.get('Samenvatting', ''),
                metadata=metadata,
                excluded_llm_metadata_keys=list(metadata.keys()),  # Exclude all metadata keys
                excluded_embed_metadata_keys=list(metadata.keys()),  # Exclude all metadata keys
                metadata_seperator="\n",
                metadata_template="{key} = {value}",
                text_template=f"Samenvatting: " + "{content}",
            )
            documents.append(document)

            print(f"\nSuccessfully created {len(documents)} documents")
        except Exception as e:
            print("\n" + "="*50)
            print("ERROR CREATING DOCUMENT")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("\nFull traceback:")
            import traceback
            print(''.join(traceback.format_tb(e.__traceback__)))
            print("="*50 + "\n")
    return documents

def embed_documents(documents: list[Document], query_collection_name: str) -> None:
    """
    Embed the documents using Cohere embeddings with retry logic and batch processing.
    """

    COHERE_API_KEY = os.getenv('COHERE_API_KEY')
    cohere_api_key = COHERE_API_KEY

    # embed model
    embed_model = CohereEmbedding(
        api_key=cohere_api_key,
        model_name="embed-english-v3.0",
        input_type="search_query",
    )
    Settings.embed_model = embed_model

    QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
    qdrant_api_key = QDRANT_API_KEY

    # creates a persistant index to disk
    client = QdrantClient(url="https://afe80cce-90ed-4adc-9aa5-f830cf036737.eu-west-1-0.aws.cloud.qdrant.io:6333",
                          api_key=qdrant_api_key,
                          timeout=3600)

    if client.collection_exists(collection_name=query_collection_name):
        print(f"Collection {query_collection_name} already exists. Deleting...")
        client.delete_collection(collection_name=query_collection_name)

    print('Starting embedding')
    start = time.time()

    # Settings for LlamaIndex
    chunk_size = 512
    chunk_overlap = 20
    Settings.chunk_size = chunk_size
    Settings.chunk_overlap = chunk_overlap
    Settings.text_splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # Add batch processing
    batch_size = 50  # Adjust this number based on your needs
    max_retries = 5
    base_delay = 60  # 60 seconds wait between retries

    # Process documents in batches
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        for attempt in range(max_retries):
            try:
                vector_store = QdrantVectorStore(
                    query_collection_name, 
                    client=client, 
                    enable_hybrid=True, 
                    batch_size=20
                )
                
                storage_context = StorageContext.from_defaults(vector_store=vector_store)

                index = VectorStoreIndex.from_documents(
                    batch,
                    storage_context=storage_context,
                    transformations=[SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)]
                )
                
                print(f"Successfully processed batch {i//batch_size + 1}")
                break  # Success, move to next batch
                
            except Exception as e:
                if "rate limit exceeded" in str(e).lower():
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        wait_time = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        print(f"Failed to process batch after {max_retries} attempts")
                        raise
                else:
                    print(f"Unexpected error: {str(e)}")
                    raise

def save_documents(documents: list[Document], save_dir: str) -> None:
    """
    Save documents to a specified directory with timestamp.
    
    Args:
        documents (list[Document]): List of documents to save
        save_dir (str): Directory path to save documents
    """
    # Create directory if it doesn't exist
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"documents_{timestamp}.pkl"
    file_path = save_path / filename
    
    # Save documents
    print(f"\nSaving {len(documents)} documents to {file_path}")
    with open(file_path, 'wb') as f:
        pickle.dump(documents, f)
    print("Documents saved successfully!")

def main():
    print("\nStarting main function...")
    start_time = time.time()
    
    # Define the paths to your JSON files
    json_paths = [
        Path("/Users/delonsaks/Documents/subsidies-dot-io/data/parse_results/parse_subsidy_text_results_national_1_20_cleaned.json"),
        # Path("../data/parse_results/parse_subsidy_text_results_national_40_60_cleaned.json"),
        # Path("../data/parse_results/parse_subsidy_text_results_national_60_74_cleaned.json"),
        # Path("../data/parse_results/parse_subsidy_text_results_regional_1_19_cleaned.json"),
        # Path("../data/parse_results/parse_subsidy_text_results_regional_38_52_cleaned.json"),
        # Path("../data/parse_results/parse_subsidy_text_results_regional_38_52_cleaned.json"),
        # Path("../data/parse_results/parse_subsidy_text_results_regional_53_65_cleaned.json"),
    ]
    
    print(f"Found {len(json_paths)} JSON files to process")
    
    # Load and combine all subsidy data
    subsidies = load_subsidy_data([str(path) for path in json_paths])

    if subsidies:
        print(f"Successfully loaded {len(subsidies)} subsidies")
        
        # Create Documents from subsidies
        print("\nStarting document creation...")
        documents = create_documents_from_subsidies(subsidies[0:5])
        print(f"Created {len(documents)} Documents")
        
        # Save documents
        save_dir = "/Users/delonsaks/Documents/subsidies-dot-io/data/vindsubsidies"
        save_documents(documents, save_dir)
        
        # Example: Print first document's text and metadata
        if documents:
            print("\nFirst document:")
            print(f"Text: {documents[0].text[:200]}...")
            print(f"Metadata: {documents[0].metadata}")
            
            query_collection_name = "vindsub_subsidies_2024_v1"
            
            # Start embedding process
            print("\nStarting embedding process...")
            try:
                embed_documents(documents, query_collection_name)
                print("Successfully completed embedding process!")
            except Exception as e:
                print(f"Error during embedding: {str(e)}")

    # Calculate and print execution time
    execution_time = time.time() - start_time
    print(f"\nTotal execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    main()
