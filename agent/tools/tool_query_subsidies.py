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

class Innovatie(BaseModel):
    """Model voor innovatie-gerelateerde subsidiecategorieën"""
    bedrijfsparticipatie: Optional[bool] = Field(
        None,
        description="Subsidies voor innovatieve bedrijfsparticipatie"
    )
    procesinnovatie: Optional[bool] = Field(
        None,
        description="Subsidies voor innovatie in bedrijfsprocessen"
    )
    productinnovatie: Optional[bool] = Field(
        None,
        description="Subsidies voor innovatie in productontwikkeling"
    )
    software: Optional[bool] = Field(
        None,
        description="Subsidies voor innovatieve software-ontwikkeling"
    )
    sociale_innovatie: Optional[bool] = Field(
        None,
        description="Subsidies voor sociale innovatie"
    )

    # class Config:
    #     title = "Innovatie Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "bedrijfsparticipatie": True,
    #             "procesinnovatie": None,
    #             "productinnovatie": True,
    #             "software": False,
    #             "sociale_innovatie": None
    #         }]
    #     }

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

    # class Config:
    #     title = "Wetenschap Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "formele_wetenschappen": True,
    #             "fundamenteel_onderzoek": None,
    #             "geesteswetenschappen": False,
    #             "geneeskunde": True,
    #             "natuurwetenschappen": None,
    #             "sociale_wetenschappen": True,
    #             "toegepast_onderzoek": False
    #         }]
    #     }

class Onderwijs(BaseModel):
    """Model voor onderwijs-gerelateerde subsidiecategorieën"""
    hoger_onderwijs: Optional[bool] = Field(
        None,
        description="Subsidies voor hoger onderwijs en universiteiten"
    )
    middelbaar_beroepsonderwijs: Optional[bool] = Field(
        None,
        description="Subsidies voor MBO-instellingen"
    )
    primair_onderwijs: Optional[bool] = Field(
        None,
        description="Subsidies voor basisonderwijs"
    )
    voortgezet_onderwijs: Optional[bool] = Field(
        None,
        description="Subsidies voor voortgezet onderwijs"
    )

    # class Config:
    #     title = "Onderwijs Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "hoger_onderwijs": True,
    #             "middelbaar_beroepsonderwijs": None,
    #             "primair_onderwijs": True,
    #             "voortgezet_onderwijs": False
    #         }]
    #     }

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
    overige_regelingen: Optional[bool] = Field(
        None,
        description="Overige onderzoeksregelingen"
    )

    # class Config:
    #     title = "Onderzoek Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "kennisoverdracht": True,
    #             "overige_regelingen": None,
    #             "innovatie": {
    #                 "bedrijfsparticipatie": True,
    #                 "procesinnovatie": None,
    #                 "productinnovatie": True
    #             },
    #             "wetenschap": {
    #                 "fundamenteel_onderzoek": True,
    #                 "toegepast_onderzoek": False
    #             }
    #         }]
    #     }


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

    # class Config:
    #     title = "Uitstroom Verbetering Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "werkervaring_evc": True,
    #             "loopbaanbegeleiding": False,
    #             "uitstroom_verbetering": True,
    #             "loonkosten": None,
    #             "vacaturevervulling": True
    #         }]
    #     }

class Arbeidsmarkt(BaseModel):
    """Model voor arbeidsmarkt-gerelateerde subsidiecategorieën"""
    activering_en_instroom: Optional[bool] = Field(
        None,
        description="Subsidies voor activering en instroom op de arbeidsmarkt"
    )
    gesubsidieerd_werk: Optional[bool] = Field(
        None,
        description="Subsidies voor gesubsidieerde arbeidsplaatsen"
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

    # class Config:
    #     title = "Arbeidsmarkt Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "activering_en_instroom": True,
    #             "gesubsidieerd_werk": None,
    #             "integratie_en_reintegratie": True,
    #             "leeftijdsbewust_beleid": False,
    #             "werknemersopleiding": True,
    #             "stages_werkleertrajecten": None,
    #             "uitstroom_verbetering": {
    #                 "werkervaring_evc": True,
    #                 "loopbaanbegeleiding": None,
    #                 "uitstroom_verbetering": True,
    #                 "loonkosten": False,
    #                 "vacaturevervulling": True
    #             }
    #         }]
    #     }

class Bouw(BaseModel):
    """Model voor bouw-gerelateerde subsidiecategorieën"""
    afwerking: Optional[bool] = Field(
        None,
        description="Subsidies voor afwerkingswerkzaamheden in de bouw"
    )
    burgerlijke_utiliteitsbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor utiliteitsbouw projecten"
    )
    civiele_techniek: Optional[bool] = Field(
        None,
        description="Subsidies voor civiele techniek projecten"
    )
    installatietechniek: Optional[bool] = Field(
        None,
        description="Subsidies voor installatietechnische werkzaamheden"
    )
    nieuwbouw: Optional[bool] = Field(
        None,
        description="Subsidies voor nieuwbouwprojecten"
    )
    renovatie: Optional[bool] = Field(
        None,
        description="Subsidies voor renovatieprojecten"
    )

    # class Config:
    #     title = "Bouw Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "afwerking": True,
    #             "burgerlijke_utiliteitsbouw": None,
    #             "civiele_techniek": True,
    #             "installatietechniek": False,
    #             "nieuwbouw": True,
    #             "renovatie": None
    #         }]
    #     }

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

    # class Config:
    #     title = "Cultuur Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "amateurkunst": True,
    #             "archieven": None,
    #             "architectuur_stedenbouw": False,
    #             "beeldende_kunst_vormgeving": True,
    #             "cultuureducatie": None,
    #             "film": True
    #         }]
    #     }

class DuurzameEnergie(BaseModel):
    """Model voor duurzame energie-gerelateerde subsidiecategorieën"""
    energiebesparing_isolatie: Optional[bool] = Field(
        None,
        description="Subsidies voor energiebesparende maatregelen en isolatie"
    )
    fossiele_energie: Optional[bool] = Field(
        None,
        description="Subsidies gerelateerd aan fossiele energiebronnen"
    )
    kernenergie: Optional[bool] = Field(
        None,
        description="Subsidies gerelateerd aan kernenergie"
    )

    # class Config:
    #     title = "Duurzame Energie Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "energiebesparing_isolatie": True,
    #             "fossiele_energie": None,
    #             "kernenergie": False
    #         }]
    #     }

class Energie(BaseModel):
    """Model voor energie-gerelateerde subsidiecategorieën"""
    duurzame_energie: Optional[DuurzameEnergie] = Field(
        None,
        description="Categorieën voor duurzame energie subsidies"
    )

    # class Config:
    #     title = "Energie Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "duurzame_energie": {
    #                 "energiebesparing_isolatie": True,
    #                 "fossiele_energie": False,
    #                 "kernenergie": None
    #             }
    #         }]
    #     }

class Export(BaseModel):
    """Model voor export-gerelateerde subsidiecategorieën"""
    export_internationalisering: Optional[bool] = Field(
        None,
        description="Subsidies voor export en internationalisering van bedrijven"
    )
    ontwikkelingssamenwerking: Optional[bool] = Field(
        None,
        description="Subsidies voor ontwikkelingssamenwerking projecten"
    )
    stedelijke_partnerschappen: Optional[bool] = Field(
        None,
        description="Subsidies voor internationale stedelijke samenwerkingsverbanden"
    )

    # class Config:
    #     title = "Export Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "export_internationalisering": True,
    #             "ontwikkelingssamenwerking": None,
    #             "stedelijke_partnerschappen": False
    #         }]
    #     }

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

    # class Config:
    #     title = "Gezondheidszorg Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "geestelijke_gezondheidszorg": True,
    #             "gehandicaptenzorg": None,
    #             "gezondheidsbescherming": True,
    #             "gezondheidszorg_ziekenhuizen": False,
    #             "zorgvoorziening": True
    #         }]
    #     }

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

    # class Config:
    #     title = "Welzijn Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "armoedebestrijding": True,
    #             "buurtwerk": None,
    #             "dierenwelzijn": False,
    #             "emancipatie": True,
    #             "gehandicapten": True,
    #             "integratie_nieuwkomers": None,
    #             "jeugd_jongeren": True,
    #             "ouderen": False,
    #             "wonen_zorg_domotica": None
    #         }]
    #     }

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

    # class Config:
    #     title = "Gezondheidszorg en Welzijn Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "gezondheidszorg": {
    #                 "geestelijke_gezondheidszorg": True,
    #                 "gehandicaptenzorg": None,
    #                 "gezondheidszorg_ziekenhuizen": False
    #             },
    #             "welzijn": {
    #                 "armoedebestrijding": True,
    #                 "jeugd_jongeren": True,
    #                 "ouderen": None
    #             }
    #         }]
    #     }

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

    # class Config:
    #     title = "ICT Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "hardware": True,
    #             "infrastructuur": None,
    #             "internet_toepassingen": True,
    #             "software": False,
    #             "telecommunicatie": None
    #         }]
    #     }

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

    # class Config:
    #     title = "Landbouw Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "akkerbouw": True,
    #             "biologische_landbouw": None,
    #             "bosbouw": False,
    #             "tuinbouw": True,
    #             "veehouderij": None
    #         }]
    #     }

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

    # class Config:
    #     title = "Visserij Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "aquacultuur": True,
    #             "visserij": None
    #         }]
    #     }

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

    # class Config:
    #     title = "Landbouw en Visserij Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "landbouw": {
    #                 "akkerbouw": True,
    #                 "biologische_landbouw": None,
    #                 "veehouderij": False
    #             },
    #             "visserij": {
    #                 "aquacultuur": True,
    #                 "visserij": None
    #             }
    #         }]
    #     }

class Milieu(BaseModel):
    """Model voor milieu-gerelateerde subsidiecategorieën"""
    afvalverwerking: Optional[bool] = Field(
        None,
        description="Subsidies voor afvalverwerking en recycling"
    )
    milieueducatie: Optional[bool] = Field(
        None,
        description="Subsidies voor milieueducatie projecten"
    )
    vervuilingsreductie: Optional[bool] = Field(
        None,
        description="Subsidies voor het verminderen van vervuiling"
    )

    # class Config:
    #     title = "Milieu Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "afvalverwerking": True,
    #             "milieueducatie": None,
    #             "vervuilingsreductie": True
    #         }]
    #     }

class Natuurbeheer(BaseModel):
    """Model voor natuurbeheer-gerelateerde subsidiecategorieën"""
    aankoop_inrichting: Optional[bool] = Field(
        None,
        description="Subsidies voor aankoop en inrichting van natuurgebieden"
    )
    beheer_onderhoud: Optional[bool] = Field(
        None,
        description="Subsidies voor beheer en onderhoud van natuurgebieden"
    )
    inrichting_functiewijziging: Optional[bool] = Field(
        None,
        description="Subsidies voor herinrichting en functiewijziging van gebieden"
    )
    soortenbescherming: Optional[bool] = Field(
        None,
        description="Subsidies voor bescherming van plant- en diersoorten"
    )

    # class Config:
    #     title = "Natuurbeheer Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "aankoop_inrichting": True,
    #             "beheer_onderhoud": None,
    #             "inrichting_functiewijziging": True,
    #             "soortenbescherming": False
    #         }]
    #     }

class OndersteunendBedrijfsleven(BaseModel):
    """Model voor bedrijfsleven-ondersteunende subsidiecategorieën"""
    groot_bedrijf: Optional[bool] = Field(
        None,
        description="Subsidies voor grote bedrijven"
    )
    mkb: Optional[bool] = Field(
        None,
        description="Subsidies voor midden- en kleinbedrijf"
    )
    starter: Optional[bool] = Field(
        None,
        description="Subsidies voor startende ondernemers"
    )
    zelfstandigen: Optional[bool] = Field(
        None,
        description="Subsidies voor zelfstandigen zonder personeel"
    )

    # class Config:
    #     title = "Ondersteunend Bedrijfsleven Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "groot_bedrijf": False,
    #             "mkb": True,
    #             "starter": True,
    #             "zelfstandigen": None
    #         }]
    #     }

class RegionaleOntwikkeling(BaseModel):
    """Model voor regionale ontwikkeling-gerelateerde subsidiecategorieën"""
    bedrijventerreinen: Optional[bool] = Field(
        None,
        description="Subsidies voor ontwikkeling van bedrijventerreinen"
    )
    plattelandsgebied: Optional[bool] = Field(
        None,
        description="Subsidies voor ontwikkeling van plattelandsgebieden"
    )
    stedelijk_gebied: Optional[bool] = Field(
        None,
        description="Subsidies voor stedelijke ontwikkeling"
    )

    # class Config:
    #     title = "Regionale Ontwikkeling Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "bedrijventerreinen": True,
    #             "plattelandsgebied": None,
    #             "stedelijk_gebied": True
    #         }]
    #     }

class Sport(BaseModel):
    """Model voor sport-gerelateerde subsidiecategorieën"""
    recreatiesport: Optional[bool] = Field(
        None,
        description="Subsidies voor recreatieve sport"
    )
    gehandicaptensport: Optional[bool] = Field(
        None,
        description="Subsidies voor gehandicaptensport"
    )
    topsport: Optional[bool] = Field(
        None,
        description="Subsidies voor topsport"
    )

    # class Config:
    #     title = "Sport Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "recreatiesport": True,
    #             "gehandicaptensport": None,
    #             "topsport": False
    #         }]
    #     }

class SportRecreatieToerisme(BaseModel):
    """Model voor sport, recreatie en toerisme-gerelateerde subsidiecategorieën"""
    recreatie_ontspanning: Optional[bool] = Field(
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

    # class Config:
    #     title = "Sport, Recreatie en Toerisme Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "recreatie_ontspanning": True,
    #             "toerisme": None,
    #             "sport": {
    #                 "recreatiesport": True,
    #                 "gehandicaptensport": None,
    #                 "topsport": False
    #             }
    #         }]
    #     }

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
    vervoer_brandstofbesparing: Optional[bool] = Field(
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

    # class Config:
    #     title = "Vervoer en Mobiliteit Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "lucht": False,
    #             "ruimtevaart": None,
    #             "spoor": True,
    #             "vervoer_brandstofbesparing": True,
    #             "water": None,
    #             "weg": False
    #         }]
    #     }

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

    # class Config:
    #     title = "Veiligheid Categorieën"
    #     json_schema_extra = {
    #         "examples": [{
    #             "brandweer_rampenbestrijding": True,
    #             "criminaliteit_veiligheid": None,
    #             "verkeersveiligheid": True,
    #             "waterkeringen": False
    #         }]
    #     }

class CategorieSelectie(BaseModel):
    """Hoofdmodel voor alle subsidiecategorieën in Nederland. 
    Wordt gebruikt voor het structureren van LLM output bij het categoriseren van subsidies."""
    
    uitstroom_verbetering: Optional[UitstroomVerbetering] = Field(
        None,
        description="Categorieën gerelateerd aan het verbeteren van uitstroom naar werk"
    )
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
    duurzame_energie: Optional[DuurzameEnergie] = Field(
        None,
        description="Duurzame energie-gerelateerde subsidiecategorieën"
    )
    energie: Optional[Energie] = Field(
        None,
        description="Energie-gerelateerde subsidiecategorieën"
    )
    export: Optional[Export] = Field(
        None,
        description="Export-gerelateerde subsidiecategorieën"
    )
    gezondheidszorg: Optional[Gezondheidszorg] = Field(
        None,
        description="Gezondheidszorg-gerelateerde subsidiecategorieën"
    )
    welzijn: Optional[Welzijn] = Field(
        None,
        description="Welzijn-gerelateerde subsidiecategorieën"
    )
    gezondheidszorg_welzijn: Optional[GezondheidszorgWelzijn] = Field(
        None,
        description="Gecombineerde gezondheidszorg en welzijn categorieën"
    )
    ict: Optional[ICT] = Field(
        None,
        description="ICT-gerelateerde subsidiecategorieën"
    )
    landbouw: Optional[Landbouw] = Field(
        None,
        description="Landbouw-gerelateerde subsidiecategorieën"
    )
    visserij: Optional[Visserij] = Field(
        None,
        description="Visserij-gerelateerde subsidiecategorieën"
    )
    landbouw_visserij: Optional[LandbouwVisserij] = Field(
        None,
        description="Gecombineerde landbouw en visserij categorieën"
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
    innovatie: Optional[Innovatie] = Field(
        None,
        description="Innovatie-gerelateerde subsidiecategorieën"
    )
    wetenschap: Optional[Wetenschap] = Field(
        None,
        description="Wetenschaps-gerelateerde subsidiecategorieën"
    )
    onderzoek: Optional[Onderzoek] = Field(
        None,
        description="Onderzoek-gerelateerde subsidiecategorieën"
    )
    regionale_ontwikkeling: Optional[RegionaleOntwikkeling] = Field(
        None,
        description="Regionale ontwikkeling-gerelateerde subsidiecategorieën"
    )
    sport: Optional[Sport] = Field(
        None,
        description="Sport-gerelateerde subsidiecategorieën"
    )
    sport_recreatie_toerisme: Optional[SportRecreatieToerisme] = Field(
        None,
        description="Sport, recreatie en toerisme-gerelateerde subsidiecategorieën"
    )
    vervoer_mobiliteit: Optional[VervoerMobiliteit] = Field(
        None,
        description="Vervoer en mobiliteit-gerelateerde subsidiecategorieën"
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