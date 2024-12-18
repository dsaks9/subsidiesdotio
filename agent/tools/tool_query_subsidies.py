from typing import List, Optional, Literal
import os
from pydantic import BaseModel, Field

from llama_index.core import Settings, Document, VectorStoreIndex, StorageContext

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

from qdrant_client import QdrantClient

from agent.tools.subsidy_report_parameters import RegionEnum, StatusEnum, REGIONS, STATUS
from agent.tools.utils import check_regions

COHERE_API_KEY = os.getenv('COHERE_API_KEY')
cohere_api_key = COHERE_API_KEY

QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
qdrant_api_key = QDRANT_API_KEY

# class SubsidyReportParameters(BaseModel):
#     """Query parameters for the subsidy report tool. Determine whether the user wants to include national level reports, where the default value
#     for include_national is True. Also, if a region or regions are provided in the text, and the region or regions are one of the valid regions,
#     include that region name. If the user requests a status and it is a valid status, include that status."""

#     include_national: bool = True
#     regions: List[str] = REGIONS
#     status: List[str] = STATUS

class SubsidyReportParameters(BaseModel):
    """Query parameters for the subsidy report tool."""
    
    include_national: Optional[Literal[True, False]] = Field(
        None, 
        description="Indicates whether the user wants to include national level subsidies or not"
    )
    regions: Optional[List[RegionEnum]] = Field(
        None, 
        description="Regions present in the input that are from the list of allowable regions"
    )
    status: Optional[List[StatusEnum]] = Field(
        None, 
        description="Status of the subsidies that the user would like to search for from the list of allowable statuses"
    )



class UitstroomVerbetering(BaseModel):
    """Model voor categorieën gerelateerd aan het verbeteren van uitstroom naar werk"""
    werkervaring_evc: Optional[bool] = Field(
        None,
        description="Subsidies voor werkervaring en Erkenning van Verworven Competenties (EVC)"
    )
    loopbaanbegeleiding: Optional[bool] = Field(
        None,
        description="Subsidies voor loopbaanadvies en -begeleiding"
    )
    uitstroom_verbetering: Optional[bool] = Field(
        None,
        description="Algemene subsidies voor het verbeteren van uitstroom naar werk"
    )
    loonkosten: Optional[bool] = Field(
        None,
        description="Subsidies voor tegemoetkoming in loonkosten"
    )
    vacaturevervulling: Optional[bool] = Field(
        None,
        description="Subsidies gericht op het vervullen van vacatures"
    )

class Arbeidsmarkt(BaseModel):
    """Model voor arbeidsmarkt-gerelateerde subsidiecategorieën"""
    activering_en_instroom: Optional[bool] = Field(
        None,
        description="Subsidies voor activering en instroom op de arbeidsmarkt"
    )
    gesubsidieerd_werk: Optional[bool] = Field(
        None,
        description="Subsidies voor gesubsidieerde arbeidsplaatsen en sociale werkvoorziening"
    )
    integratie_en_reintegratie: Optional[bool] = Field(
        None,
        description="Subsidies voor (re)integratie trajecten"
    )
    leeftijdsbewust_beleid: Optional[bool] = Field(
        None,
        description="Subsidies voor leeftijdsbewust personeelsbeleid"
    )
    werknemersopleiding: Optional[bool] = Field(
        None,
        description="Subsidies voor het opleiden van werknemers"
    )
    uitstroom_verbetering: Optional[UitstroomVerbetering] = Field(
        None,
        description="Specifieke uitstroom verbeteringsmaatregelen"
    )
    stages_werkleertrajecten: Optional[bool] = Field(
        None,
        description="Subsidies voor stages en werkleertrajecten"
    )

class Bouw(BaseModel):
    """Model voor bouw-gerelateerde subsidiecategorieën"""
    afwerking: Optional[bool] = Field(
        None,
        description="Subsidies voor afwerkingswerkzaamheden in de bouw (zoals schilders en stukadoors)"
    )
    burgerlijke_utiliteitsbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor utiliteitsbouw projecten (bouw van woningen, kantoren en dergelijke)"
    )
    grond_weg_waterbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor grond-, weg- en waterbouw (GWW)"
    )
    installatietechniek: Optional[bool] = Field(
        None,
        description="Subsidies voor installatietechnische werkzaamheden (elektrische installaties, verwarming en dergelijke)"
    )
    nieuwbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor nieuwbouwprojecten"
    )
    renovatie: Optional[bool] = Field(
        None,
        description="Subsidies voor renovatieprojecten"
    )

class Cultuur(BaseModel):
    """Model voor cultuur-gerelateerde subsidiecategorieën"""
    amateurkunst: Optional[bool] = Field(
        None,
        description="Subsidies voor amateurkunstbeoefening"
    )
    archieven: Optional[bool] = Field(
        None,
        description="Subsidies voor archiefbeheer en -ontsluiting"
    )
    architectuur_stedenbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor architectuur en stedenbouwkundige projecten"
    )
    beeldende_kunst_vormgeving: Optional[bool] = Field(
        None,
        description="Subsidies voor beeldende kunst en vormgeving"
    )
    cultuureducatie: Optional[bool] = Field(
        None,
        description="Subsidies voor cultuureducatieve projecten"
    )
    dans: Optional[bool] = Field(
        None,
        description="Subsidies voor dansproducties"
    )
    film: Optional[bool] = Field(
        None,
        description="Subsidies voor filmproducties en -vertoning"
    )
    landschapsarchitectuur: Optional[bool] = Field(
        None,
        description="Subsidies voor landschapsarchitectuur"
    )
    letteren_bibliotheken: Optional[bool] = Field(
        None,
        description="Subsidies voor letterkundige projecten en bibliotheken"
    )
    media: Optional[bool] = Field(
        None,
        description="Subsidies voor mediaprojecten"
    )
    monumenten_erfgoed_archeologie: Optional[bool] = Field(
        None,
        description="Subsidies voor monumentenzorg, erfgoed en archeologie"
    )
    musea: Optional[bool] = Field(
        None,
        description="Subsidies voor musea"
    )
    muziek_muziektheater: Optional[bool] = Field(
        None,
        description="Subsidies voor muziek en muziektheater"
    )
    theater: Optional[bool] = Field(
        None,
        description="Subsidies voor theaterproducties"
    )


class DuurzameEnergie(BaseModel):
    """Model voor duurzame energie-gerelateerde subsidiecategorieën"""
    bio_energie: Optional[bool] = Field(
        None,
        description="Subsidies voor bio-energie"
    )
    geothermische_energie: Optional[bool] = Field(
        None,
        description="Subsidies voor geothermische energie"
    )
    waterenergie: Optional[bool] = Field(
        None,
        description="Subsidies voor waterenergie"
    )
    windenergie: Optional[bool] = Field(
        None,
        description="Subsidies voor windenergie"
    )
    zonne_energie_fotovoltaische_energie: Optional[bool] = Field(
        None,
        description="Subsidies voor zonne-energie en fotovoltaïsche energie"
    )


class EnergieEnDuurzaamheid(BaseModel):
    """Model voor energie en duurzaamheid-gerelateerde subsidiecategorieën"""
    duurzame_energie: Optional[DuurzameEnergie] = Field(
        None,
        description="Categorieën voor duurzame energie subsidies"
    )
    energiebesparing_isolatie_en_verduurzaming: Optional[bool] = Field(
        None,
        description="Subsidies voor energiebesparing, isolatie en verduurzaming"
    )
    fossiele_energie: Optional[bool] = Field(
        None,
        description="Subsidies voor fossiele energie (aardolie, aardgas, steenkool en bruinkool)"
    )
    kernenergie: Optional[bool] = Field(
        None,
        description="Subsidies voor kernenergie"
    )


class ExportEnInternationalisering(BaseModel):
    """Model voor export en internationalisering-gerelateerde subsidiecategorieën"""
    export_krediet_verzekering_garantie: Optional[bool] = Field(
        None,
        description="Subsidies voor export krediet, verzekering en garantie"
    )
    internationalisering: Optional[bool] = Field(
        None,
        description="Subsidies voor internationalisering"
    )
    promotionele_activiteiten: Optional[bool] = Field(
        None,
        description="Subsidies voor promotionele activiteiten"
    )


class ExportInternationaliseringOntwikkelingssamenwerking(BaseModel):
    """Model voor export, internationalisering en ontwikkelingssamenwerking-gerelateerde subsidiecategorieën"""
    export_en_internationalisering: Optional[ExportEnInternationalisering] = Field(
        None,
        description="Export en internationalisering-gerelateerde subsidiecategorieën"
    )
    ontwikkelingssamenwerking: Optional[bool] = Field(
        None,
        description="Subsidies voor ontwikkelingssamenwerking projecten"
    )
    stedenbanden_en_uitwisseling: Optional[bool] = Field(
        None,
        description="Subsidies voor stedenbanden en uitwisseling met andere overheden"
    )


class Gezondheidszorg(BaseModel):
    """Model voor gezondheidszorg-gerelateerde subsidiecategorieën"""
    geestelijke_gezondheidszorg: Optional[bool] = Field(
        None,
        description="Subsidies voor geestelijke gezondheidszorg"
    )
    gehandicaptenzorg: Optional[bool] = Field(
        None,
        description="Subsidies voor gehandicaptenzorg"
    )
    gezondheidsbescherming: Optional[bool] = Field(
        None,
        description="Subsidies voor gezondheidsbescherming"
    )
    gezondheidszorg_ziekenhuizen: Optional[bool] = Field(
        None,
        description="Subsidies voor ziekenhuizen en algemene gezondheidszorg"
    )
    zorgvoorziening: Optional[bool] = Field(
        None,
        description="Subsidies voor zorgvoorzieningen"
    )


class Welzijn(BaseModel):
    """Model voor welzijn-gerelateerde subsidiecategorieën"""
    armoedebestrijding: Optional[bool] = Field(
        None,
        description="Subsidies voor armoedebestrijding en schuldhulpverlening"
    )
    buurtwerk: Optional[bool] = Field(
        None,
        description="Subsidies voor buurtwerk en sociale cohesie"
    )
    dierenwelzijn: Optional[bool] = Field(
        None,
        description="Subsidies voor dierenwelzijn projecten"
    )
    emancipatie: Optional[bool] = Field(
        None,
        description="Subsidies voor emancipatie en gelijke kansen"
    )
    gehandicapten: Optional[bool] = Field(
        None,
        description="Subsidies voor gehandicaptenvoorzieningen"
    )
    integratie_nieuwkomers: Optional[bool] = Field(
        None,
        description="Subsidies voor integratie van nieuwkomers"
    )
    jeugd_jongeren: Optional[bool] = Field(
        None,
        description="Subsidies voor jeugd- en jongerenwerk"
    )
    ouderen: Optional[bool] = Field(
        None,
        description="Subsidies voor ouderenzorg en -voorzieningen"
    )
    wonen_zorg_domotica: Optional[bool] = Field(
        None,
        description="Subsidies voor wonen, zorg en domotica"
    )

class GezondheidszorgWelzijn(BaseModel):
    """Model voor gecombineerde gezondheidszorg en welzijn categorieën"""
    gezondheidszorg: Optional[Gezondheidszorg] = Field(
        None,
        description="Gezondheidszorg-gerelateerde subsidiecategorieën"
    )
    welzijn: Optional[Welzijn] = Field(
        None,
        description="Welzijn-gerelateerde subsidiecategorieën"
    )


class ICT(BaseModel):
    """Model voor ICT-gerelateerde subsidiecategorieën"""
    hardware: Optional[bool] = Field(
        None,
        description="Subsidies voor hardware-gerelateerde projecten"
    )
    infrastructuur: Optional[bool] = Field(
        None,
        description="Subsidies voor ICT-infrastructuur"
    )
    internet_toepassingen: Optional[bool] = Field(
        None,
        description="Subsidies voor internet en web-applicaties"
    )
    software: Optional[bool] = Field(
        None,
        description="Subsidies voor software-ontwikkeling"
    )
    telecommunicatie: Optional[bool] = Field(
        None,
        description="Subsidies voor telecommunicatie projecten"
    )


class Landbouw(BaseModel):
    """Model voor landbouw-gerelateerde subsidiecategorieën"""
    akkerbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor akkerbouw projecten"
    )
    biologische_landbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor biologische landbouw"
    )
    bosbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor bosbouw en bosonderhoud"
    )
    tuinbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor tuinbouw projecten"
    )
    veehouderij: Optional[bool] = Field(
        None,
        description="Subsidies voor veehouderij"
    )


class Visserij(BaseModel):
    """Model voor visserij-gerelateerde subsidiecategorieën"""
    aquacultuur: Optional[bool] = Field(
        None,
        description="Subsidies voor aquacultuur projecten"
    )
    visserij: Optional[bool] = Field(
        None,
        description="Subsidies voor visserij activiteiten"
    )


class LandbouwVisserij(BaseModel):
    """Model voor gecombineerde landbouw en visserij categorieën"""
    landbouw: Optional[Landbouw] = Field(
        None,
        description="Landbouw-gerelateerde subsidiecategorieën"
    )
    visserij: Optional[Visserij] = Field(
        None,
        description="Visserij-gerelateerde subsidiecategorieën"
    )

class Levensbeschouwing(BaseModel):
    """Model voor levensbeschouwing-gerelateerde subsidiecategorieën"""
    levensbeschouwing: Optional[bool] = Field(
        None,
        description="Subsidies voor levensbeschouwelijke activiteiten en organisaties"
    )
    
class Milieu(BaseModel):
    """Model voor milieu-gerelateerde subsidiecategorieën"""
    afvalverwijdering_opslag_waterzuivering: Optional[bool] = Field(
        None,
        description="Subsidies voor afvalverwijdering en -opslag, waterzuivering"
    )
    milieueducatie_voorlichting: Optional[bool] = Field(
        None,
        description="Subsidies voor milieueducatie, voorlichting"
    )
    vermindering_vervuiling: Optional[bool] = Field(
        None,
        description="Subsidies voor vermindering vervuiling bodem, geluid, water en lucht"
    )


class Natuurbeheer(BaseModel):
    """Model voor natuurbeheer-gerelateerde subsidiecategorieën"""
    aankoop_en_aanleg: Optional[bool] = Field(
        None,
        description="Subsidies voor aankoop en aanleg van natuurgebieden"
    )
    beheer_en_instandhouding: Optional[bool] = Field(
        None,
        description="Subsidies voor beheer en instandhouding van natuurgebieden"
    )
    inrichting_en_functieverandering: Optional[bool] = Field(
        None,
        description="Subsidies voor inrichting en functieverandering van gebieden"
    )
    soortenbescherming_en_biodiversiteit: Optional[bool] = Field(
        None,
        description="Subsidies voor soortenbescherming en biodiversiteit"
    )


class OndersteunendBedrijfsleven(BaseModel):
    """Model voor bedrijfsleven-ondersteunende subsidiecategorieën"""
    ondersteuning_grote_onderneming: Optional[bool] = Field(
        None,
        description="Subsidies voor grote bedrijven"
    )
    ondersteuning_mkb: Optional[bool] = Field(
        None,
        description="Subsidies voor midden- en kleinbedrijf"
    )
    ondersteuning_starter: Optional[bool] = Field(
        None,
        description="Subsidies voor startende ondernemers"
    )
    ondersteuning_zelfstandige: Optional[bool] = Field(
        None,
        description="Subsidies voor zelfstandigen zonder personeel"
    )

class Onderwijs(BaseModel):
    """Model voor onderwijs-gerelateerde subsidiecategorieën"""
    hoger_en_universitair_onderwijs: Optional[bool] = Field(
        None,
        description="Subsidies voor hoger en universitair onderwijs (hbo en universiteit)"
    )
    middelbaar_beroepsonderwijs_en_volwasseneneducatie: Optional[bool] = Field(
        None,
        description="Subsidies voor middelbaar beroepsonderwijs en volwasseneneducatie (BVE)"
    )
    primair_onderwijs: Optional[bool] = Field(
        None,
        description="Subsidies voor primair onderwijs"
    )
    voortgezet_onderwijs: Optional[bool] = Field(
        None,
        description="Subsidies voor voortgezet onderwijs (praktijkonderwijs, vmbo, leerwegondersteunend onderwijs, havo en vwo)"
    )

class Innovatie(BaseModel):
    """Model voor innovatie-gerelateerde subsidiecategorieën"""
    deelname_bedrijfsleven_aan_onderzoek: Optional[bool] = Field(
        None,
        description="Subsidies voor deelname bedrijfsleven aan onderzoek"
    )
    procesinnovatie: Optional[bool] = Field(
        None,
        description="Subsidies voor innovatie in bedrijfsprocessen"
    )
    productinnovatie: Optional[bool] = Field(
        None,
        description="Subsidies voor innovatie in productontwikkeling"
    )
    programmatuur: Optional[bool] = Field(
        None,
        description="Subsidies voor innovatieve programmatuur"
    )
    sociale_innovatie: Optional[bool] = Field(
        None,
        description="Subsidies voor sociale innovatie"
    )

class Wetenschap(BaseModel):
    """Model voor wetenschaps-gerelateerde subsidiecategorieën"""
    formele_wetenschappen: Optional[bool] = Field(
        None,
        description="Subsidies voor formele wetenschappen"
    )
    fundamenteel_onderzoek: Optional[bool] = Field(
        None,
        description="Subsidies voor fundamenteel wetenschappelijk onderzoek"
    )
    geesteswetenschappen: Optional[bool] = Field(
        None,
        description="Subsidies voor geesteswetenschappen"
    )
    geneeskunde: Optional[bool] = Field(
        None,
        description="Subsidies voor geneeskundig onderzoek"
    )
    natuurwetenschappen: Optional[bool] = Field(
        None,
        description="Subsidies voor natuurwetenschappelijk onderzoek"
    )
    sociale_wetenschappen: Optional[bool] = Field(
        None,
        description="Subsidies voor sociaal-wetenschappelijk onderzoek"
    )
    toegepast_onderzoek: Optional[bool] = Field(
        None,
        description="Subsidies voor toegepast wetenschappelijk onderzoek"
    )

class Onderzoek(BaseModel):
    """Model voor onderzoek-gerelateerde subsidiecategorieën"""
    innovatie: Optional[Innovatie] = Field(
        None,
        description="Innovatie-gerelateerde subsidiecategorieën"
    )
    kennisoverdracht: Optional[bool] = Field(
        None,
        description="Subsidies voor kennisoverdracht en -verspreiding"
    )
    wetenschap: Optional[Wetenschap] = Field(
        None,
        description="Wetenschaps-gerelateerde subsidiecategorieën"
    )

class OverigeRegelingen(BaseModel):
    """Model voor overige regelingen die niet in andere categorieën passen"""
    overige_regelingen: Optional[bool] = Field(
        None,
        description="Subsidies die niet in andere categorieën passen"
    )


class RegionaleOntwikkeling(BaseModel):
    """Model voor regionale ontwikkeling-gerelateerde subsidiecategorieën"""
    bedrijventerreinen: Optional[bool] = Field(
        None,
        description="Subsidies voor ontwikkeling van bedrijventerreinen"
    )
    landelijk_gebied: Optional[bool] = Field(
        None,
        description="Subsidies voor plattelandsontwikkeling"
    )
    stedelijk_gebied: Optional[bool] = Field(
        None,
        description="Subsidies voor stedelijke vernieuwing"
    )


class Sport(BaseModel):
    """Model voor sport-gerelateerde subsidiecategorieën"""
    breedtesport: Optional[bool] = Field(
        None,
        description="Subsidies voor breedtesport"
    )
    gehandicaptensport: Optional[bool] = Field(
        None,
        description="Subsidies voor gehandicaptensport"
    )
    topsport: Optional[bool] = Field(
        None,
        description="Subsidies voor topsport"
    )


class SportRecreatieToerisme(BaseModel):
    """Model voor sport, recreatie en toerisme-gerelateerde subsidiecategorieën"""
    recreatie_en_ontspanning: Optional[bool] = Field(
        None,
        description="Subsidies voor recreatie en ontspanning"
    )
    sport: Optional[Sport] = Field(
        None,
        description="Sport-gerelateerde subsidiecategorieën"
    )
    toerisme: Optional[bool] = Field(
        None,
        description="Subsidies voor toerisme"
    )


class VervoerMobiliteit(BaseModel):
    """Model voor vervoer en mobiliteit-gerelateerde subsidiecategorieën"""
    lucht: Optional[bool] = Field(
        None,
        description="Subsidies voor luchtvaart"
    )
    ruimtevaart: Optional[bool] = Field(
        None,
        description="Subsidies voor ruimtevaart"
    )
    spoor: Optional[bool] = Field(
        None,
        description="Subsidies voor spoorwegen"
    )
    transport_en_brandstofbesparing: Optional[bool] = Field(
        None,
        description="Subsidies voor brandstofbesparing in transport"
    )
    water: Optional[bool] = Field(
        None,
        description="Subsidies voor watervervoer"
    )
    weg: Optional[bool] = Field(
        None,
        description="Subsidies voor wegvervoer"
    )

class Veiligheid(BaseModel):
    """Model voor veiligheid-gerelateerde subsidiecategorieën"""
    brandweer_rampenbestrijding: Optional[bool] = Field(
        None,
        description="Subsidies voor brandweer en rampenbestrijding"
    )
    criminaliteit_veiligheid: Optional[bool] = Field(
        None,
        description="Subsidies voor criminaliteitspreventie en veiligheid"
    )
    verkeersveiligheid: Optional[bool] = Field(
        None,
        description="Subsidies voor verkeersveiligheid"
    )
    waterkeringen: Optional[bool] = Field(
        None,
        description="Subsidies voor waterkeringen en waterveiligheid"
    )


class CategorieSelectie(BaseModel):
    """Hoofdmodel voor alle subsidiecategorieën in Nederland. 
    Wordt gebruikt voor het structureren van LLM output bij het categoriseren van subsidies."""
    
    arbeidsmarkt: Optional[Arbeidsmarkt] = Field(
        None,
        description="Arbeidsmarkt-gerelateerde subsidiecategorieën"
    )
    bouw: Optional[Bouw] = Field(
        None,
        description="Bouw-gerelateerde subsidiecategorieën"
    )
    cultuur: Optional[Cultuur] = Field(
        None,
        description="Cultuur-gerelateerde subsidiecategorieën"
    )
    energie: Optional[EnergieEnDuurzaamheid] = Field(
        None,
        description="Energie en duurzaamheid-gerelateerde subsidiecategorieën"
    )
    export_internationalisering_ontwikkelingssamenwerking: Optional[ExportInternationaliseringOntwikkelingssamenwerking] = Field(
        None,
        description="Export, internationalisering en ontwikkelingssamenwerking-gerelateerde subsidiecategorieën"
    )
    gezondheidszorg_welzijn: Optional[GezondheidszorgWelzijn] = Field(
        None,
        description="Gecombineerde gezondheidszorg en welzijn categorieën"
    )
    ict: Optional[ICT] = Field(
        None,
        description="ICT-gerelateerde subsidiecategorieën"
    )
    landbouw_visserij: Optional[LandbouwVisserij] = Field(
        None,
        description="Gecombineerde landbouw en visserij categorieën"
    )
    levensbeschouwing: Optional[Levensbeschouwing] = Field(
        None,
        description="Levensbeschouwing-gerelateerde subsidiecategorieën"
    )
    milieu: Optional[Milieu] = Field(
        None,
        description="Milieu-gerelateerde subsidiecategorieën"
    )
    natuurbeheer: Optional[Natuurbeheer] = Field(
        None,
        description="Natuurbeheer-gerelateerde subsidiecategorieën"
    )
    ondersteunend_bedrijfsleven: Optional[OndersteunendBedrijfsleven] = Field(
        None,
        description="Bedrijfsleven-ondersteunende subsidiecategorieën"
    )
    onderwijs: Optional[Onderwijs] = Field(
        None,
        description="Onderwijs-gerelateerde subsidiecategorieën"
    )
    onderzoek: Optional[Onderzoek] = Field(
        None,
        description="Onderzoek-gerelateerde subsidiecategorieën"
    )
    overige_regelingen: Optional[OverigeRegelingen] = Field(
        None,
        description="Overige regelingen die niet in andere categorieën passen"
    )
    regionale_ontwikkeling: Optional[RegionaleOntwikkeling] = Field(
        None,
        description="Regionale ontwikkeling-gerelateerde subsidiecategorieën"
    )
    sport_recreatie_toerisme: Optional[SportRecreatieToerisme] = Field(
        None,
        description="Sport, recreatie en toerisme-gerelateerde subsidiecategorieën"
    )
    transport_mobiliteit: Optional[VervoerMobiliteit] = Field(
        None,
        description="Transport en mobiliteit-gerelateerde subsidiecategorieën"
    )
    veiligheid: Optional[Veiligheid] = Field(
        None,
        description="Veiligheid-gerelateerde subsidiecategorieën"
    )

    # class Config:
    #     title = "Subsidie Categorie Selectie"
    #     json_schema_extra = {
    #         "examples": [{
    #             "arbeidsmarkt": {
    #                 "activering_en_instroom": True,
    #                 "gesubsidieerd_werk": None,
    #                 "integratie_en_reintegratie": True,
    #                 "uitstroom_verbetering": {
    #                     "werkervaring_evc": True,
    #                     "loopbaanbegeleiding": None
    #                 }
    #             },
    #             "onderwijs": {
    #                 "hoger_onderwijs": True,
    #                 "middelbaar_beroepsonderwijs": False
    #             },
    #             "innovatie": {
    #                 "bedrijfsparticipatie": True,
    #                 "procesinnovatie": None
    #             }
    #         }]
    #     }


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

    # if player_description:
    #     nodes = retriever.retrieve(player_description)
    #     nodes = st.session_state.postprocessor.postprocess_nodes(nodes=nodes, query_str=player_description)
    # else:
    #     nodes = retriever.retrieve(' ')

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