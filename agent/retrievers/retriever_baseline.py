import os

from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.core.program import FunctionCallingProgram
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core import Settings, Document, VectorStoreIndex, StorageContext
from llama_index.postprocessor.cohere_rerank import CohereRerank

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

    nodes = retriever.retrieve(user_input)
    nodes = postprocessor.postprocess_nodes(nodes=nodes, query_str=user_input)

    return nodes
if __name__ == "__main__":
    user_input = input("Please enter your subsidy query: ")
    nodes = retrieve_subsidies(user_input)
    print(nodes)
