import os
from typing import List

from llama_index.core.program import FunctionCallingProgram
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core import Settings, Document, VectorStoreIndex, StorageContext
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.core.schema import NodeWithScore

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, MatchAny

from agent.prompts.prompts import SYSTEM_PROMPT_NATIONAL_REGION_STATUS_EXTRACTOR
from agent.tools.subsidy_report_parameters import REGIONS, STATUS

from agent.tools.tool_query_subsidies import query_subsidies, SubsidyReportParameters, CategorieSelectie
from agent.tools.utils import check_regions

from openai import OpenAI

### tracers ###

from phoenix.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
# Add Phoenix API Key for tracing
PHOENIX_API_KEY = os.getenv('PHOENIX_API_KEY')
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={PHOENIX_API_KEY}"

# configure the Phoenix tracer
tracer_provider = register(
  project_name="my-llm-app", # Default is 'default'
  endpoint="https://app.phoenix.arize.com/v1/traces",
)

LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

from openinference.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

### end tracers ###

COHERE_API_KEY = os.getenv('COHERE_API_KEY')
cohere_api_key = COHERE_API_KEY

QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
qdrant_api_key = QDRANT_API_KEY


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OpenAI.api_key = OPENAI_API_KEY

client_openai = OpenAI()


# # prompt_template_str = """\
# You are an expert system designed to analyze user requests about Dutch subsidies and extract structured parameters for subsidy searches. Your task is to carefully analyze the given input and determine the appropriate search parameters according to the provided data model.

# Key Parameters to Extract:

# 1. National Level Inclusion (include_national):
# - Set to True if the user explicitly wants national subsidies
# - Set to False if the user explicitly excludes national subsidies
# - Set to None if not specified

# 2. Regions (regions):
# Valid regions are:
# - Drenthe
# - Flevoland
# - Friesland
# - Gelderland
# - Groningen
# - Limburg
# - Noord-Brabant
# - Noord-Holland
# - Overijssel
# - Utrecht
# - Zeeland
# - Zuid-Holland

# 3. Status (status):
# Valid statuses are:
# - Open
# - Aangekondigd
# - Gesloten

# Analysis Guidelines:
# 1. Read the input carefully and identify any mentions of:
#    - Geographic scope (national/regional preferences)
#    - Specific regions
#    - Desired subsidy status

# 2. For geographic parameters:
#    - Look for explicit mentions of national vs. regional preferences
#    - Identify any specific regions mentioned
#    - Validate regions against the allowed list
#    - Handle multiple regions if mentioned

# 3. For status parameters:
#    - Identify any mentions of subsidy status
#    - Validate against allowed status values
#    - Handle multiple status values if mentioned

# Please provide your response in the following format:

# Analysis:
# [Provide a brief analysis of what you identified in the input]

# Extracted Parameters:
# [List the specific parameters you identified and why]

# JSON Output:
# {
#     "include_national": [true/false/null],
#     "regions": ["Region1", "Region2"],
#     "status": ["Status1", "Status2"]
# }

# Important Notes:
# - Only include parameters that are clearly indicated in the input
# - Use null/None for parameters that aren't specified
# - Ensure all regions match exactly with the allowed values
# - Ensure all status values match exactly with the allowed values
# - The output must be valid according to the following Pydantic model

# Analyze the user input below and extract the parameters:
# <user_input>
# {user_input}
# </user_input>
# """

# def extract_query_parameters(user_input: str):

#     program = FunctionCallingProgram.from_defaults(
#         output_cls=SubsidyReportParameters, 
#         prompt_template_str=prompt_template_str, 
#         verbose=True
#     )
    
#     output = program(user_input=user_input)
    
#     include_national = output.include_national
#     regions = output.regions
#     status = output.status
    
#     return include_national, regions, status

def extract_parameters(user_input: str) -> str:
    """
    Extract the category from the summary of a subsidy.
    """

    summary_extraction_system_prompt = SYSTEM_PROMPT_NATIONAL_REGION_STATUS_EXTRACTOR

    completion = client_openai.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": summary_extraction_system_prompt},
        {"role": "user", "content": user_input},
    ],
    response_format=SubsidyReportParameters,
    )

    report_parameters = completion.choices[0].message.parsed

    include_national = report_parameters.include_national

    if report_parameters.regions:
        regions = [region.value for region in report_parameters.regions]
    else:
        regions = None

    if report_parameters.status:
        status = [status.value for status in report_parameters.status]
    else:
        status = None

    return include_national, regions, status


# def retrieve_subsidies(user_input):
#     include_national, regions, status = extract_parameters(user_input)

#     filter_conditions = []

#     query_locations = []
#     if include_national:
#         query_locations.append('National')
#     if regions:
#         query_locations.extend(regions)

#     if query_locations:
#         filter_conditions.append(
#             FieldCondition(
#                 key="Bereik",
#                 match=MatchAny(any=query_locations),
#             )
#         )

#     if status:
#         filter_conditions.append(
#             FieldCondition(
#                 key="Status",
#                 match=MatchAny(any=status),
#             )
#         )

#     # Combine all conditions into a single Filter
#     combined_filter = Filter(
#         must=filter_conditions
#     ) if filter_conditions else None

#     print(f'combined_filter: {combined_filter}')

#     # embed model
#     embed_model = CohereEmbedding(
#         api_key=cohere_api_key,
#         model_name="embed-english-v3.0",
#         input_type="search_query",
#     )
#     Settings.embed_model = embed_model

#     postprocessor = CohereRerank(
#         top_n=5,
#         model="rerank-v3.5",
#         api_key=cohere_api_key,
#     )

#     client = QdrantClient(url="https://afe80cce-90ed-4adc-9aa5-f830cf036737.eu-west-1-0.aws.cloud.qdrant.io:6333",
#                           api_key=qdrant_api_key,
#                           timeout=3600)
    
#     query_collection_name = "vindsub_subsidies_2024_v1"
#     vector_store = QdrantVectorStore(
#                 query_collection_name, 
#                 client=client, 
#                 enable_hybrid=True)

#     index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

#     if combined_filter:
#         retriever = index.as_retriever(similarity_top_k=100, vector_store_kwargs={"qdrant_filters": combined_filter})
#     else:
#         retriever = index.as_retriever(similarity_top_k=100)

#     nodes_embed = retriever.retrieve(user_input)
#     nodes_reranked = postprocessor.postprocess_nodes(nodes=nodes_embed, query_str=user_input)

#     return nodes_reranked, nodes_embed

def retrieve_subsidies(
    query: str, 
    include_national: bool = True, 
    regions: List[str] = None, 
    categories: dict = None,
    status: List[str] = None
):
    """
    Retrieve subsidies based on query and filters
    """
    try:
        # Convert the categories dict to CategorieSelectie model
        category_filters = CategorieSelectie(**categories) if categories else None
        
        filter_conditions = []

        query_locations = []
        if include_national:
            query_locations.append('National')
        if regions:
            query_locations.extend(regions)

        if query_locations:
            filter_conditions.append(
                FieldCondition(
                    key="Bereik",
                    match=MatchAny(any=query_locations),
                )
            )

        if status:
            filter_conditions.append(
                FieldCondition(
                    key="Status",
                    match=MatchAny(any=status),
                )
            )

        if category_filters:
            category_conditions = []
            
            # Process each main category
            for main_category, subcategories in category_filters.__dict__.items():
                if isinstance(subcategories, dict):  # Only process if it's a dictionary
                    # Check if the main category itself is selected (all subcategories should match)
                    if any(isinstance(v, bool) and v for v in subcategories.values()):
                        # Create conditions for all possible subcategories under this main category
                        subcategory_conditions = []
                        for sub_key, sub_value in subcategories.items():
                            if isinstance(sub_value, dict):
                                # Handle nested subcategories (e.g., uitstroom_verbetering)
                                for nested_key, _ in sub_value.items():
                                    subcategory_conditions.append(
                                        FieldCondition(
                                            key=f"categories.{main_category}.{sub_key}.{nested_key}",
                                            match=MatchValue(value=True)
                                        )
                                    )
                            else:
                                subcategory_conditions.append(
                                    FieldCondition(
                                        key=f"categories.{main_category}.{sub_key}",
                                        match=MatchValue(value=True)
                                    )
                                )
                        # Add an OR condition for any subcategory
                        if subcategory_conditions:
                            category_conditions.append(
                                Filter(
                                    should=subcategory_conditions,
                                    min_should_match=1  # Match at least one subcategory
                                )
                            )
                    else:
                        # Process specific selected subcategories
                        for sub_key, sub_value in subcategories.items():
                            if isinstance(sub_value, dict):
                                # Handle nested subcategories (e.g., uitstroom_verbetering)
                                for nested_key, nested_value in sub_value.items():
                                    if nested_value:  # Only add if True
                                        category_conditions.append(
                                            FieldCondition(
                                                key=f"categories.{main_category}.{sub_key}.{nested_key}",
                                                match=MatchValue(value=True)
                                            )
                                        )
                            elif sub_value:  # Only add if True
                                category_conditions.append(
                                    FieldCondition(
                                        key=f"categories.{main_category}.{sub_key}",
                                        match=MatchValue(value=True)
                                    )
                                )
            
            # Add category conditions with OR logic if any exist
            if category_conditions:
                filter_conditions.append(
                    Filter(
                        should=category_conditions
                    )
                )

        # Add location filter
        query_locations = []
        if include_national:
            query_locations.append('National')
        if regions:
            query_locations.extend(regions)

        if query_locations:
            filter_conditions.append(
                FieldCondition(
                    key="Bereik",
                    match=MatchAny(any=query_locations)
                )
            )

        if status:
            filter_conditions.append(
                FieldCondition(
                    key="Status",
                    match=MatchAny(any=status)
                )
            )

        # Combine all conditions into a single Filter with AND logic
        combined_filter = Filter(
            must=filter_conditions
        ) if filter_conditions else None

        print(f'combined_filter: {combined_filter}')

        # embed model
        embed_model = CohereEmbedding(
            api_key=cohere_api_key,
            model_name="embed-english-v3.0",
            input_type="search_query",
        )
        Settings.embed_model = embed_model

        postprocessor = CohereRerank(
            top_n=5,
            model="rerank-v3.5",
            api_key=cohere_api_key,
        )

        client = QdrantClient(url="https://afe80cce-90ed-4adc-9aa5-f830cf036737.eu-west-1-0.aws.cloud.qdrant.io:6333",
                            api_key=qdrant_api_key,
                            timeout=3600)
        
        query_collection_name = "vindsub_subsidies_2024_v1"
        vector_store = QdrantVectorStore(
                    query_collection_name, 
                    client=client, 
                    enable_hybrid=True)

        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        if combined_filter:
            retriever = index.as_retriever(similarity_top_k=100, vector_store_kwargs={"qdrant_filters": combined_filter})
        else:
            retriever = index.as_retriever(similarity_top_k=100)

        nodes_embed = retriever.retrieve(user_input)
        nodes_reranked = postprocessor.postprocess_nodes(nodes=nodes_embed, query_str=user_input)

        return nodes_reranked, nodes_embed
        
    except Exception as e:
        raise Exception(f"Error in retrieve_subsidies: {str(e)}")

def check_nodes_for_subsidy(subsidy_titles: List[str], nodes: List[NodeWithScore]):
    matching_nodes = []
    for index, node in enumerate(nodes):
        if node.node.metadata.get('title') in subsidy_titles:
            matching_nodes.append((node.node.metadata.get('title'), index))
    return matching_nodes if matching_nodes else []

if __name__ == "__main__":

    user_input = """
Veel communicatie gebeurt via beeld en schrift. Denk aan TV, computer, tablets, smartphones, maar ook via informatieborden op rijkswegen en in openbare gebouwen. Helaas zijn grote groepen mensen beperkt in het begrijpen van deze vormen van communicatie. Blinden en slechtzienden, ouderen, dementerenden maar ook analfabeten en mensen afkomstig uit andere landen kunnen vaak niet uit de voeten met geschreven tekst..Doel van dit project is het ontwikkelen van “drukwerk” met geprinte geluidsmodules voor mensen met lichamelijke beperkingen zoals slechtziendheid, blindheid of niet aangeboren hersenletsel en voor mensen met geestelijke beperkingen op het gebied van kijken of begrijpend lezen. Toepassing van de geprinte geluidsmodules zijn voorzien voor het gebruik van farmaceutische producten en in producten en diensten voor de zorg als ondersteuning van bijsluiters, gebruiksaanwijzingen of als alarmering voor medicatie. De ontwikkelde technologie kan, geprint op een kaart, als zelfstandig communicatiemiddel worden ingezet, gecombineerd worden met computers, terminals, smartphones, tablets etc. maar kan ook geïntegreerd worden toegepast in verpakkingen. Binnen het project is de ontwikkeling voorzien van:.- Gesproken geheugen.- of medicijninnamekaart voor verschillende doelgroepen..- Gesproken medicijnkaart/bijsluiter voor blinden en slechtzienden, eventueel geïntegreerd in de verpakking..- Gesproken “spraakkaart” voor analfabeten (dit kan een bijsluiter voor medicijnen zijn maar ook een gesproken routebeschrijving voor openbare gebouwen of ziekenhuizen)..- Gesproken geheugen ondersteuning voor mensen met Dementie..- Gesproken Stimulans kaart voor mensen met dementie (kan ook in combinatie met een beeldschermpje via software matig gekoppelde apparaten).
"""

    if not user_input:
        user_input = input("Please enter your subsidy query: ")

    nodes_reranked, nodes_embed = retrieve_subsidies(user_input)

    subsidy_titles = [
        "Mkb Innovatiestimulering Topsectoren (TKI mkb-versterking en Mkb Innovatiestimulering Topsectoren - MIT) - Regeling nationale EZK- en LNV-subsidies -",
        "Wet vermindering afdracht loonbelasting en premie voor de volksverzekeringen"
    ]

    if not subsidy_titles:
        subsidy_titles = input("Please enter the subsidy titles to check: ")

    matching_nodes_embed = check_nodes_for_subsidy(subsidy_titles, nodes_embed)
    matching_nodes_reranked = check_nodes_for_subsidy(subsidy_titles, nodes_reranked)
    print(f'matching_nodes - nodes_embed: {matching_nodes_embed}')
    print(f'matching_nodes - nodes_reranked: {matching_nodes_reranked}')
