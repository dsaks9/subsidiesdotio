from typing import List
import os
from pydantic import BaseModel

from llama_index.core import Settings, Document, VectorStoreIndex, StorageContext

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

from qdrant_client import QdrantClient

from agent.tools.subsidy_report_parameters import REGIONS, STATUS
from agent.tools.utils import check_regions

COHERE_API_KEY = os.getenv('COHERE_API_KEY')
cohere_api_key = COHERE_API_KEY

QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
qdrant_api_key = QDRANT_API_KEY

class SubsidyReportParameters(BaseModel):
    """Query parameters for the subsidy report tool. Determine whether the user wants to include national level reports, where the default value
    for include_national is True. Also, if a region or regions are provided in the text, and the region or regions are one of the valid regions,
    include that region name. If the user requests a status and it is a valid status, include that status."""

    include_national: bool = True
    regions: List[str] = REGIONS
    status: List[str] = STATUS

def query_subsidies(
        include_national: bool = True,
        regions: List[str] = REGIONS,
        status: List[str] = STATUS,
        ) -> str:
    """Use this tool to query a database of subsidies using descriptive attributes and provide those subsidies. 
    The descriptive attributes must be from provided information and not prior knowledge."""
    
    # input checking
    regions = check_regions(regions)

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

    if player_description:
        nodes = retriever.retrieve(player_description)
        nodes = st.session_state.postprocessor.postprocess_nodes(nodes=nodes, query_str=player_description)
    else:
        nodes = retriever.retrieve(' ')

    output_parts = [
        f"""
        <player_evaluation>
        The player evaluation done by the scout named <scout_name>{node.metadata['scout']}</scout_name> for the baseball player named <player_name>{node.metadata['player_name']}</player_name> is shown here:
        date of evaluation: {node.metadata['last_seen']}
        draft_year: {node.metadata['draft_year']}
        position: {node.metadata['pos']}
        dollar_value_range: {node.metadata['value_range']}
        school_level: {node.metadata['school_level']}
        summary: {node.text}
        </player_evaluation>
        """.strip()
        for node in nodes
    ]

    output = '\n\n'.join(output_parts)
    output_message = f'The following player evaluations were retrieved:\n\n{output}'

    return output_message