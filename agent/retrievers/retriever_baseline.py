import os
from typing import List

from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.core.program import FunctionCallingProgram
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core import Settings, Document, VectorStoreIndex, StorageContext
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.core.schema import NodeWithScore

from qdrant_client import QdrantClient

from agent.prompts.prompts import SYSTEM_PROMPT_SUBSIDY_REPORT_AGENT

from agent.tools.tool_query_subsidies import query_subsidies, SubsidyReportParameters
from agent.tools.utils import check_regions


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

COHERE_API_KEY = os.getenv('COHERE_API_KEY')
cohere_api_key = COHERE_API_KEY

QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
qdrant_api_key = QDRANT_API_KEY

prompt_template_str = """\
Extract the query parameters from the user's input.
<user_input>
{user_input}
</user_input>
"""

def extract_query_parameters(user_input: str):

    program = FunctionCallingProgram.from_defaults(
        output_cls=SubsidyReportParameters, 
        prompt_template_str=prompt_template_str, 
        verbose=True
    )
    
    output = program(user_input=user_input)
    
    include_national = output.include_national
    regions = output.regions
    status = output.status
    
    return include_national, regions, status


def retrieve_subsidies(user_input):
    include_national, regions, status = extract_query_parameters(user_input)

    filters = []

    query_locations = []
    if include_national:
        query_locations.append('National')
    if regions:
        query_locations.extend(regions)

    if query_locations:
        filters.append(MetadataFilter(key="Bereik", operator=FilterOperator.IN, value=query_locations))

    if status:
        filters.append(MetadataFilter(key="Status", operator=FilterOperator.IN, value=status))

    filters_db = MetadataFilters(filters=filters) if filters else None

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

    # creates a persistant index to disk
    client = QdrantClient(url="https://afe80cce-90ed-4adc-9aa5-f830cf036737.eu-west-1-0.aws.cloud.qdrant.io:6333",
                          api_key=qdrant_api_key,
                          timeout=3600)
    
    query_collection_name = "vindsub_subsidies_2024_v1"
    vector_store = QdrantVectorStore(
                query_collection_name, 
                client=client, 
                enable_hybrid=True)

    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    if filters_db:
        retriever = index.as_retriever(similarity_top_k=100, filters=filters_db)
    else:
        retriever = index.as_retriever(similarity_top_k=100)

    nodes_embed = retriever.retrieve(user_input)
    nodes_reranked = postprocessor.postprocess_nodes(nodes=nodes_embed, query_str=user_input)

    return nodes_reranked, nodes_embed

def check_nodes_for_subsidy(subsidy_titles: List[str], nodes: List[NodeWithScore]):
    matching_nodes = []
    for index, node in enumerate(nodes):
        if node.node.metadata.get('title') in subsidy_titles:
            matching_nodes.append((node.node.metadata.get('title'), index))
    return matching_nodes if matching_nodes else []

if __name__ == "__main__":

    user_input = """
In the hot milling steel industry there is a strong need for a measurement device that can determine whether the steel plates leaving het milling machine are according specs. As the sheets are leaving the machine under tension and high temperatures, standard thickness measurements is not sufficient to determine whether the plates are produced correctly, as when the pressure releases and the prodcut has cooled down, it might happen some unwanted wrinkles defects will appear again in the product, making the plates nog useful anymore for commercial use. Today it can take up to tens of minutes before any defect can be detected and the machine is adjusted accordingly. In the meantime, as the output speed of the material is several meters per second, a lot of metal needs to be scrapped/reproduced as a result of the delay. Whitin this development project we are going to develop and build a proof of concept of the worlds first flatness in line measuring roll based on interferometric fiber optic measurement technology. This measurement roll will be able to work in the ambient conditions given I hot strip rolling facilities, working at temperatures of up to 600C. The measurement roll will be placed richt after the machine and finally will be used to provide input to the pressing process inside the milling machine (controlled loop system). The main critical steps in the project consist of the development of the high temperature fiber optic sensors, the fiber network inside the role, the measurement roll itself including the rotating fiber output, the development of the optical readout to this application and the design of the algorithm that converse measurement output to input the hot milling machine controls. The final goal is the development of a new inline flatness measuring roll for hot rolling for the European metal industry, and to transfer the technology into a worldwide available product. Witt this approach, the decade-long existing hurdle to measure the shape of metal strips in the hot rolling process can be overcome and provides this essential quality measure in the very first step of production of sheet metal, allowing for immediate control and correction actions and thus improved yield and less scrap material.
"""

    if not user_input:
        user_input = input("Please enter your subsidy query: ")
    nodes_reranked, nodes_embed = retrieve_subsidies(user_input)

    subsidy_titles = [
        "Versnelde klimaatinvesteringen in de industrie - Regeling nationale EZK- en LNV-subsidies -",
    ]

    if not subsidy_titles:
        subsidy_titles = input("Please enter the subsidy titles to check: ")

    matching_nodes_embed = check_nodes_for_subsidy(subsidy_titles, nodes_embed)
    matching_nodes_reranked = check_nodes_for_subsidy(subsidy_titles, nodes_reranked)
    print(f'matching_nodes - nodes_embed: {matching_nodes_embed}')
    print(f'matching_nodes - nodes_reranked: {matching_nodes_reranked}')
