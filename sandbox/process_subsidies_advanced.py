# process_subsidies_advanced.py

import pandas as pd
from openai import OpenAI
import os
import time
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import List
from enum import Enum
from datetime import datetime

# Load environment variables from .env file
load_dotenv()
client = OpenAI()

# Configure logging
logging.basicConfig(
    filename='process_subsidies.log',
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

# Define Pydantic Models for Structured Extraction

class Categorie(Enum):
    klimaat_energie = "klimaat & Energie"
    landbouw = "landbouw"
    ondernemen_bedrijfsvoering = "ondernemen & bedrijfsvoering"
    bouwen_wonen = "bouwen & wonen"
    visserij = "visserij"
    gezondheid_zorg_welzijn = "gezondheid, zorg & welzijn"
    internationaal_ondernemen = "internationaal ondernemen"
    dier_natuur = "dier & natuur"
    ontwikkelingssamenwerking = "ontwikkelingssamenwerking"
    innovatie_onderzoek_onderwijs = "innovatie, onderzoek & onderwijs"

class Target(Enum):
    MKB_Startup = "MKB / startup"
    kennisinstelling = "kennisinstelling"
    groot_bedrijf = "groot_bedrijf"
    overheid = "overheid / gemeente / NGO"
    consument = "consument"
    
class SubsidieData(BaseModel):
    voorwaarden: str
    categorie: Categorie
    target: Target
    max_budget: str
    max_subsidie: str
    aanmeldproces: str

# Summarization Prompt
summarization_prompt = '''
## Rol
Je bent een subsidie expert met meer dan 20 jaar ervaring. 

## Taak
De gebruiker stuurt markdown content van een internet pagina met informatie over een subsidie. Extraheer de informatie over de subsidie / regeling. 
Gebruik de voorbeelden om een goede samenvatting te maken.

## Details
Zorg dat de volgende informatie in je output staat: 
- Korte beschrijving van de subsidie: deze kun je vaak direct uit de webpagina halen
- Korte beschrijving voor wie de subsidie bedoeld is. Denk hier aan type organisatie(s), consortia, locatie van aanvragers, sector, etc
- Korte beschrijving wat het doel is van de subsidieverstrekker met de subsidie / regeling
- Beschrijving van de (type) kosten die je terug of vergoed krijgt van de subsidieverstrekker

## Voorbeelden:
<voorbeeld 1>
De DHI-subsidieregeling (Demonstratieprojecten) biedt organisaties de mogelijkheid om een technologie, product of dienst te demonstreren in een van de DHI-landen. De organisatie demonstreert een eigen technologie, product of dienst die in Nederland is ontwikkeld en geproduceerd. Het doel is om aan meerdere lokale partijen te bewijzen dat de technologie, het product of de dienst effectief en rendabel is, wat kan leiden tot contracten. Het lukt de organisatie niet om op korte termijn en op eigen kracht de markt te betreden, omdat de buitenlandse markten en de complexiteit daarvan niet bekend zijn. De organisatie heeft ondersteuning nodig om de nieuwe markt te betreden.

### Voor wie is de subsidie bedoeld?
De subsidie is bedoeld voor mkb-ondernemingen in Nederland en het Caribische deel van het Koninkrijk met internationale ambities. Grotere ondernemingen kunnen ook in aanmerking komen, mits zij samenwerken met een Nederlandse mkb-onderneming als penvoerder. De aanvragen moeten betrekking hebben op demonstratieprojecten in specifieke DHI-landen.

### Doel van de subsidieverstrekker
Het doel van de subsidieverstrekker is om Nederlandse technologieën, producten of diensten te introduceren en te bewijzen in buitenlandse markten, met als uiteindelijke doel het stimuleren van export en het versterken van de internationale positie van Nederlandse bedrijven.

### Kosten die vergoed worden
Met de DHI-regeling kan 50% tot 70% van de kosten van het demonstratieproject worden gefinancierd, met een maximum van € 200.000. De kosten die in aanmerking komen voor subsidie zijn onder andere de directe kosten van de demonstratie, maar geen kosten voor ontwikkeling, marktonderzoek of aanpassingen aan de technologie. De minimale subsidie bedraagt € 25.000, wat betekent dat de kosten minimaal € 50.000 moeten zijn.
</voorbeeld 1>

<voorbeeld 2>
De WBSO (Wet Bevordering Speur- en Ontwikkelingswerk) is een fiscale regeling die ondernemers belastingvoordeel biedt wanneer zij aan Research & Development (R&D) doen of technisch-wetenschappelijk onderzoek uitvoeren.

### Voor wie is de subsidie bedoeld?
De subsidie is bedoeld voor ondernemers in Nederland die zelf nieuwe programmatuur, producten of productieprocessen ontwikkelen, of technisch-wetenschappelijk onderzoek uitvoeren. Dit geldt voor zowel zelfstandigen als ondernemingen met personeel, mits het project plaatsvindt binnen de Europese Unie.

### Doel van de subsidieverstrekker
Het doel van de WBSO is om de kosten van speur- en ontwikkelingswerk (S&O) voor ondernemers te verlagen, zodat innovaties en onderzoeksprojecten gestimuleerd worden. De regeling is bedoeld om de concurrentiekracht van Nederlandse bedrijven te versterken door hen te ondersteunen in hun R&D-activiteiten.

### Kosten die vergoed worden
De WBSO vergoedt een deel van de loonkosten van S&O-projecten. Ondernemingen met personeel kunnen daarnaast een aftrek ontvangen over andere kosten en uitgaven van het S&O-project, zoals de inkoop van materialen. De exacte percentages voor de aftrek zijn afhankelijk van de schijven en bedragen die jaarlijks worden vastgesteld. In 2025 is het tarief voor de eerste schijf 32% en voor starters 40%, met een grens van €350.000 voor de S&O-grondslag.
</voorbeeld 2>

Haal diep adem en denk stap voor stap. Haal alleen informatie uit de webpagina en berust je niet op eerdere kennis!
'''

# Structured Output Prompt
structured_output_prompt = '''
### ROL
JE BENT EEN ERVAREN SUBSIDIEADVISEUR GESPECIALISEERD IN HET ANALYSEREN EN STRUCTUREREN VAN SUBSIDIEGEGEVENS. 
JE HEBT JARENLANGE ERVARING IN HET LEZEN EN INTERPRETEREN VAN SUBSIDIE INFORMATIE VAN WEBPAGINA'S OM NAUWKEURIGE EN VOLLEDIGE DATASETS OVER SUBSIDIES TE MAKEN.

### INSTRUCTIES
EXTRAHEER NAUWKEURIG DE BENODIGDE GEGEVENS OVER EEN SUBSIDIE UIT EEN MARKDOWN-TEKST EN PRESENTEER DEZE IN EEN GESTRUCTUREERD JSON-OBJECT VOLGENS HET OPGEGEVEN DATAMODEL. 
ZORG ERVOOR DAT DE DATA ALLEEN AFKOMSTIG IS VAN DE INFORMATIE OP DE WEBPAGINA EN GEEN VERZONNEN DETAILS BEVAT.

### OUTPUT
voorwaarden: een opsomming van alle voorwaarden om de subsidie te krijgen
categorie: de categorie van de subsidie, deze is exact te vinden in de markdown, bedenk het niet zelf
target: voor wie de subsidie / regeling bedoelt is. 
max_budget: het totale budget van de subsidie uit de beschikbare informatie. Beschrijf in één zin het exacte bedrag of geef aan waar het budget van afhankelijk is.
max_subsidie: Duidelijke beschrijving van het maximale bedrag, voordeel of aftrek waar één organisatie gebruik van kan maken binnen het subsidieprogramma. Formuleer in één zin het maximale bedrag of geef aan waar het van afhankelijk is.
aanmeldproces: Beschrijving van het aanmeldproces. Waar moet je inschrijven, welke infromatie, formulieren of andere benodigdheden horen daarbij

### Wat Niet Te Doen
OBEY en never do:
- NOOIT ONNODIGE INFORMATIE opnemen die niet direct gerelateerd is aan de gevraagde gegevens.
- NOOIT FOUTIEVE CATEGORISATIE van gegevens onder de verkeerde `Categorie` enum.
- NOOIT INCOMPLETE OF INCORRECTE DATA presenteren in de JSON-output.
- NOOIT INFORMATIE VERWAARLOZEN die vereist is voor het opbouwen van een volledig `Subsidie` object.
- NOOIT TITLE CASE GEBRUIKEN in kopjes. Gebruik alleen hoofdletters wanneer grammaticaal correct.
'''

def summarize_markdown(markdown_text):
    """
    Sends markdown content to OpenAI for summarization.

    Parameters:
    - markdown_text (str): The markdown content to summarize.

    Returns:
    - str: The summary generated by OpenAI.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": summarization_prompt},
                {"role": "user", "content": markdown_text}
            ],
            temperature=0.3,
            max_tokens=500
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        return "Error during summarization."

def extract_structured_data(markdown_text):
    """
    Extracts structured data from markdown content using OpenAI's response_format parameter.

    Parameters:
    - markdown_text (str): The markdown content to extract data from.

    Returns:
    - SubsidieData: An instance of SubsidieData containing the extracted information.
    """
    try:
        # Utilize the response_format parameter to directly parse the response into SubsidieData
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",  # Ensure this model supports response_format
            temperature=0,
            messages=[
                {"role": "system", "content": structured_output_prompt},
                {"role": "user", "content": markdown_text}
            ],
            response_format=SubsidieData,  # Directly map the response to the Pydantic model
        )
        return completion.choices[0].message
    except ValidationError as ve:
        logging.error(f"Pydantic validation error: {ve}")
        return None
    except Exception as e:
        logging.error(f"Error during structured extraction: {e}")
        return None

def main():
    current_date = datetime.now().strftime('%Y-%m-%d')
    INPUT_CSV = r"C:\Users\caski\OneDrive\Documents\Gaido\Subsidies\DB scraping 2\venv\RVO subsidiewijzer\subsidies_processed_2024-12-02.csv"
    OUTPUT_CSV = f'subsidies_final{current_date}.csv'
    SUMMARY_COLUMN = 'summary'
    RATE_LIMIT_PER_MIN = 5000  # Adjust as per OpenAI's rate limits
    SECONDS_PER_REQUEST = 60 / RATE_LIMIT_PER_MIN  

    # Check if input CSV exists
    if not os.path.isfile(INPUT_CSV):
        logging.error(f"Input CSV file '{INPUT_CSV}' not found.")
        print(f"Error: Input CSV file '{INPUT_CSV}' not found. Please ensure the file is in the current directory.")
        return

    # Read the processed CSV
    try:
        df = pd.read_csv(INPUT_CSV)
        logging.info(f"Successfully read CSV file: {INPUT_CSV}")
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        print(f"Error: Failed to read CSV file. Check logs for details.")
        return

    # Check for 'Markdown_content' column
    if 'Markdown_content' not in df.columns:
        logging.error("'Markdown_content' column not found in the CSV.")
        print("Error: 'Markdown_content' column not found in the CSV.")
        return

    # Initialize new columns
    df['summary'] = ""
    df['voorwaarden'] = ""
    df['categorie'] = ""
    df['target'] = ""
    df['max_budget'] = ""
    df['max_subsidie'] = ""
    df['aanmeldproces'] = ""

    total_rows = len(df)
    logging.info(f"Starting advanced processing of {total_rows} rows.")
    print(f"Starting advanced processing of {total_rows} rows.")

    for index, row in df.iterrows():
        markdown = row['Markdown_content']
        logging.info(f"Processing row {index + 1}/{total_rows}")
        print(f"Processing row {index + 1}/{total_rows}")

        # Step 1: Summarization
        summary = summarize_markdown(markdown)
        df.at[index, 'summary'] = summary

        # Rate limiting
        time.sleep(SECONDS_PER_REQUEST)

        # Step 2: Structured Extraction
        subsidie_data = extract_structured_data(markdown).parsed
        if subsidie_data:
            df.at[index, 'voorwaarden'] = subsidie_data.voorwaarden
            df.at[index, 'categorie'] = subsidie_data.categorie
            df.at[index, 'target'] = subsidie_data.target
            df.at[index, 'max_budget'] = subsidie_data.max_budget
            df.at[index, 'max_subsidie'] = subsidie_data.max_subsidie
            df.at[index, 'aanmeldproces'] = subsidie_data.aanmeldproces
        else:
            df.at[index, 'voorwaarden'] = "Extraction failed."
            df.at[index, 'categorie'] = "Extraction failed."
            df.at[index, 'max_budget'] = "Extraction failed."
            df.at[index, 'max_subsidie'] = "Extraction failed."
            df.at[index, 'aanmeldproces'] = "Extraction failed."

        # Rate limiting
        time.sleep(SECONDS_PER_REQUEST)

    # Save the final dataframe
    try:
        df.to_csv(OUTPUT_CSV, index=False)
        logging.info(f"Successfully saved the final processed data to {OUTPUT_CSV}")
        print(f"Successfully saved the final processed data to {OUTPUT_CSV}")
    except Exception as e:
        logging.error(f"Failed to save the final CSV: {e}")
        print(f"Error: Failed to save the final CSV. Check logs for details.")

if __name__ == "__main__":
    main()
