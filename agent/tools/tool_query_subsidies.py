from typing import List, Optional
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

from pydantic import BaseModel
from typing import List, Optional

# Geneste categoriemodellen
class UitstroomVerbetering(BaseModel):
    werkervaring_evc: bool = False
    loopbaanbegeleiding: bool = False
    uitstroom_verbetering: bool = False
    loonkosten: bool = False
    vacaturevervulling: bool = False

class Arbeidsmarkt(BaseModel):
    activering_en_instroom: bool = False
    gesubsidieerd_werk: bool = False
    integratie_en_reintegratie: bool = False
    leeftijdsbewust_beleid: bool = False
    werknemersopleiding: bool = False
    uitstroom_verbetering: Optional[UitstroomVerbetering] = None
    stages_werkleertrajecten: bool = False

class Bouw(BaseModel):
    afwerking: bool = False
    burgerlijke_utiliteitsbouw: bool = False
    civiele_techniek: bool = False
    installatietechniek: bool = False
    nieuwbouw: bool = False
    renovatie: bool = False

class Cultuur(BaseModel):
    amateurkunst: bool = False
    archieven: bool = False
    architectuur_stedenbouw: bool = False
    beeldende_kunst_vormgeving: bool = False
    cultuureducatie: bool = False
    film: bool = False
    landschapsarchitectuur: bool = False
    letteren_bibliotheken: bool = False
    media: bool = False
    monumenten_erfgoed_archeologie: bool = False
    musea: bool = False
    muziek_muziektheater: bool = False
    theater: bool = False

class DuurzameEnergie(BaseModel):
    energiebesparing_isolatie: bool = False
    fossiele_energie: bool = False
    kernenergie: bool = False

class Energie(BaseModel):
    duurzame_energie: Optional[DuurzameEnergie] = None

class Export(BaseModel):
    export_internationalisering: bool = False
    ontwikkelingssamenwerking: bool = False
    stedelijke_partnerschappen: bool = False

class Gezondheidszorg(BaseModel):
    geestelijke_gezondheidszorg: bool = False
    gehandicaptenzorg: bool = False
    gezondheidsbescherming: bool = False
    gezondheidszorg_ziekenhuizen: bool = False
    zorgvoorziening: bool = False

class Welzijn(BaseModel):
    armoedebestrijding: bool = False
    buurtwerk: bool = False
    dierenwelzijn: bool = False
    emancipatie: bool = False
    gehandicapten: bool = False
    integratie_nieuwkomers: bool = False
    jeugd_jongeren: bool = False
    ouderen: bool = False
    wonen_zorg_domotica: bool = False

class GezondheidszorgWelzijn(BaseModel):
    gezondheidszorg: Optional[Gezondheidszorg] = None
    welzijn: Optional[Welzijn] = None

class ICT(BaseModel):
    hardware: bool = False
    infrastructuur: bool = False
    internet_toepassingen: bool = False
    software: bool = False
    telecommunicatie: bool = False

class Landbouw(BaseModel):
    akkerbouw: bool = False
    biologische_landbouw: bool = False
    bosbouw: bool = False
    tuinbouw: bool = False
    veehouderij: bool = False

class Visserij(BaseModel):
    aquacultuur: bool = False
    visserij: bool = False

class LandbouwVisserij(BaseModel):
    landbouw: Optional[Landbouw] = None
    visserij: Optional[Visserij] = None

class Milieu(BaseModel):
    afvalverwerking: bool = False
    milieueducatie: bool = False
    vervuilingsreductie: bool = False

class Natuurbeheer(BaseModel):
    aankoop_inrichting: bool = False
    beheer_onderhoud: bool = False
    inrichting_functiewijziging: bool = False
    soortenbescherming: bool = False

class OndersteunendBedrijfsleven(BaseModel):
    groot_bedrijf: bool = False
    mkb: bool = False
    starter: bool = False
    zelfstandigen: bool = False

class Onderwijs(BaseModel):
    hoger_onderwijs: bool = False
    middelbaar_beroepsonderwijs: bool = False
    primair_onderwijs: bool = False
    voortgezet_onderwijs: bool = False

class Innovatie(BaseModel):
    bedrijfsparticipatie: bool = False
    procesinnovatie: bool = False
    productinnovatie: bool = False
    software: bool = False
    sociale_innovatie: bool = False

class Wetenschap(BaseModel):
    formele_wetenschappen: bool = False
    fundamenteel_onderzoek: bool = False
    geesteswetenschappen: bool = False
    geneeskunde: bool = False
    natuurwetenschappen: bool = False
    sociale_wetenschappen: bool = False
    toegepast_onderzoek: bool = False

class Onderzoek(BaseModel):
    innovatie: Optional[Innovatie] = None
    kennisoverdracht: bool = False
    wetenschap: Optional[Wetenschap] = None
    overige_regelingen: bool = False

class RegionaleOntwikkeling(BaseModel):
    bedrijventerreinen: bool = False
    plattelandsgebied: bool = False
    stedelijk_gebied: bool = False

class Sport(BaseModel):
    recreatiesport: bool = False
    gehandicaptensport: bool = False
    topsport: bool = False

class SportRecreatieToerisme(BaseModel):
    recreatie_ontspanning: bool = False
    sport: Optional[Sport] = None
    toerisme: bool = False

class VervoerMobiliteit(BaseModel):
    lucht: bool = False
    ruimtevaart: bool = False
    spoor: bool = False
    vervoer_brandstofbesparing: bool = False
    water: bool = False
    weg: bool = False

class Veiligheid(BaseModel):
    brandweer_rampenbestrijding: bool = False
    criminaliteit_veiligheid: bool = False
    verkeersveiligheid: bool = False
    waterkeringen: bool = False

class CategorieSelectie(BaseModel):
    uitstroom_verbetering: Optional[UitstroomVerbetering] = None
    arbeidsmarkt: Optional[Arbeidsmarkt] = None
    bouw: Optional[Bouw] = None
    cultuur: Optional[Cultuur] = None
    duurzame_energie: Optional[DuurzameEnergie] = None
    energie: Optional[Energie] = None
    export: Optional[Export] = None
    gezondheidszorg: Optional[Gezondheidszorg] = None
    welzijn: Optional[Welzijn] = None
    gezondheidszorg_welzijn: Optional[GezondheidszorgWelzijn] = None
    ict: Optional[ICT] = None
    landbouw: Optional[Landbouw] = None
    visserij: Optional[Visserij] = None
    landbouw_visserij: Optional[LandbouwVisserij] = None
    milieu: Optional[Milieu] = None
    natuurbeheer: Optional[Natuurbeheer] = None
    ondersteunend_bedrijfsleven: Optional[OndersteunendBedrijfsleven] = None
    onderwijs: Optional[Onderwijs] = None
    innovatie: Optional[Innovatie] = None
    wetenschap: Optional[Wetenschap] = None
    onderzoek: Optional[Onderzoek] = None
    regionale_ontwikkeling: Optional[RegionaleOntwikkeling] = None
    sport: Optional[Sport] = None
    sport_recreatie_toerisme: Optional[SportRecreatieToerisme] = None
    vervoer_mobiliteit: Optional[VervoerMobiliteit] = None
    veiligheid: Optional[Veiligheid] = None


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