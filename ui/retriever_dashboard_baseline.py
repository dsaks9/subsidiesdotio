import streamlit as st
from agent.retrievers.retriever_baseline import retrieve_subsidies
from agent.tools.subsidy_report_parameters import REGIONS
from agent.tools.tool_query_subsidies import CategorieSelectie
import traceback
import logging

# Set up logging at the top of your file
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def display_node(node):
    """Helper function to display a single node's information"""
    metadata = node.node.metadata
    score = node.score
    
    # Create expandable section for each subsidy
    with st.expander(f"📋 {metadata.get('title', 'Untitled')} - Score: {score:.3f}"):
        # Display key metadata in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Status:**", metadata.get('Status', 'N/A'))
            st.write("**Bereik:**", metadata.get('Bereik', 'N/A'))
            st.write("**Deadline:**", metadata.get('Deadline', 'N/A'))
            
        with col2:
            st.write("**Min. bijdrage:**", metadata.get('Minimale bijdrage', 'N/A'))
            st.write("**Max. bijdrage:**", metadata.get('Maximale bijdrage', 'N/A'))
            st.write("**Budget:**", metadata.get('Budget', 'N/A'))
        
        # Display the text content
        st.markdown("**Relevante informatie:**")
        st.write(node.node.text)
        
        # Additional metadata without nested expander
        st.markdown("---")
        st.markdown("**Extra details:**")
        st.write("**Laatste wijziging:**", metadata.get('Laatste wijziging', 'N/A'))
        st.write("**Aanvraagtermijn:**", metadata.get('Aanvraagtermijn', 'N/A'))
        st.write("**Indienprocedure:**", metadata.get('Indienprocedure', 'N/A'))

def main():
    # Set page config
    st.set_page_config(
        page_title="Subsidie Zoeker",
        page_icon="🔍",
        layout="wide"
    )
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Status filter
        selected_status = st.multiselect(
            "Status",
            options=["Open", "Aangekondigd", "Gesloten"],
            default=[]
        )
        
        # National/Regional filter
        include_national = st.checkbox("Inclusief nationale subsidies", value=True)
        
        # Region selection
        selected_regions = st.multiselect(
            "Selecteer regio('s)",
            options=REGIONS,
            default=[]
        )
        
        # Category selection
        st.subheader("Categorieën")
        
        # Create tabs for each main category
        tab_names = [
            "Arbeidsmarkt",
            "Bouw",
            "Cultuur",
            "Energie en Duurzaamheid",
            "Export, Internationalisering & Ontwikkelingssamenwerking",
            "Gezondheidszorg & Welzijn",
            "ICT",
            "Landbouw & Visserij",
            "Levensbeschouwing",
            "Milieu",
            "Natuurbeheer",
            "Ondersteunend Bedrijfsleven",
            "Onderwijs",
            "Onderzoek",
            "Regionale Ontwikkeling",
            "Sport, Recreatie & Toerisme",
            "Transport & Mobiliteit",
            "Veiligheid"
        ]
        
        tabs = st.tabs(tab_names)
        category_filters = {}
        
        with tabs[0]:  # Arbeidsmarkt
            if st.checkbox("Arbeidsmarkt"):
                st.markdown("##### Arbeidsmarkt subcategorieën")
                category_filters['arbeidsmarkt'] = {
                    'activering_en_instroom': st.checkbox("Activering en instroom", key="arbeidsmarkt_activering"),
                    'gesubsidieerd_werk': st.checkbox("Gesubsidieerd werk", key="arbeidsmarkt_gesubsidieerd"),
                    'integratie_en_reintegratie': st.checkbox("Integratie en reïntegratie", key="arbeidsmarkt_integratie"),
                    'leeftijdsbewust_beleid': st.checkbox("Leeftijdsbewust beleid", key="arbeidsmarkt_leeftijd"),
                    'werknemersopleiding': st.checkbox("Werknemersopleiding", key="arbeidsmarkt_opleiding"),
                    'stages_werkleertrajecten': st.checkbox("Stages en werkleertrajecten", key="arbeidsmarkt_stages")
                }
                
                # Uitstroom verbetering subcategory
                if st.checkbox("Uitstroom verbetering", key="arbeidsmarkt_uitstroom"):
                    st.markdown("###### Uitstroom verbetering subcategorieën")
                    category_filters['arbeidsmarkt']['uitstroom_verbetering'] = {
                        'werkervaring_evc': st.checkbox("Werkervaring en EVC", key="uitstroom_werkervaring"),
                        'loopbaanbegeleiding': st.checkbox("Loopbaanbegeleiding", key="uitstroom_loopbaan"),
                        'uitstroom_verbetering': st.checkbox("Algemene uitstroom verbetering", key="uitstroom_algemeen"),
                        'loonkosten': st.checkbox("Loonkosten", key="uitstroom_loonkosten"),
                        'vacaturevervulling': st.checkbox("Vacaturevervulling", key="uitstroom_vacature")
                    }

        with tabs[1]:  # Bouw
            if st.checkbox("Bouw"):
                st.markdown("##### Bouw subcategorieën")
                category_filters['bouw'] = {
                    'afwerking': st.checkbox("Afwerking"),
                    'burgerlijke_utiliteitsbouw': st.checkbox("Burgerlijke utiliteitsbouw"),
                    'grond_weg_waterbouw': st.checkbox("Grond-, weg- en waterbouw"),
                    'installatietechniek': st.checkbox("Installatietechniek"),
                    'nieuwbouw': st.checkbox("Nieuwbouw"),
                    'renovatie': st.checkbox("Renovatie")
                }

        with tabs[2]:  # Cultuur
            if st.checkbox("Cultuur"):
                st.markdown("##### Cultuur subcategorieën")
                category_filters['cultuur'] = {
                    'amateurkunst': st.checkbox("Amateurkunst"),
                    'archieven': st.checkbox("Archieven"),
                    'architectuur_stedenbouw': st.checkbox("Architectuur en stedenbouw"),
                    'beeldende_kunst_vormgeving': st.checkbox("Beeldende kunst en vormgeving"),
                    'cultuureducatie': st.checkbox("Cultuureducatie"),
                    'dans': st.checkbox("Dans"),
                    'film': st.checkbox("Film"),
                    'landschapsarchitectuur': st.checkbox("Landschapsarchitectuur"),
                    'letteren_bibliotheken': st.checkbox("Letteren en bibliotheken"),
                    'media': st.checkbox("Media"),
                    'monumenten_erfgoed_archeologie': st.checkbox("Monumenten, erfgoed en archeologie"),
                    'musea': st.checkbox("Musea"),
                    'muziek_muziektheater': st.checkbox("Muziek en muziektheater"),
                    'theater': st.checkbox("Theater")
                }

        with tabs[3]:  # Energie en Duurzaamheid
            if st.checkbox("Energie en Duurzaamheid"):
                st.markdown("##### Energie en Duurzaamheid subcategorieën")
                category_filters['energie_en_duurzaamheid'] = {}
                
                # Duurzame energie subcategory
                if st.checkbox("Duurzame energie", key="energie_duurzaam"):
                    st.markdown("###### Duurzame energie subcategorieën")
                    category_filters['energie_en_duurzaamheid']['duurzame_energie'] = {
                        'bio_energie': st.checkbox("Bio-energie", key="energie_bio"),
                        'geothermische_energie': st.checkbox("Geothermische energie", key="energie_geo"),
                        'waterenergie': st.checkbox("Waterenergie", key="energie_water"),
                        'windenergie': st.checkbox("Windenergie", key="energie_wind"),
                        'zonne_energie_fotovoltaische_energie': st.checkbox("Zonne-energie en fotovoltaïsche energie", key="energie_zon")
                    }
                
                # Other categories
                category_filters['energie_en_duurzaamheid'].update({
                    'energiebesparing_isolatie_en_verduurzaming': st.checkbox("Energiebesparing, isolatie en verduurzaming", key="energie_besparing"),
                    'fossiele_energie': st.checkbox("Fossiele energie", key="energie_fossiel"),
                    'kernenergie': st.checkbox("Kernenergie", key="energie_kern")
                })

        with tabs[4]:  # Export, Internationalisering & Ontwikkelingssamenwerking
            if st.checkbox("Export, Internationalisering & Ontwikkelingssamenwerking"):
                st.markdown("##### Export, Internationalisering & Ontwikkelingssamenwerking subcategorieën")
                category_filters['export_internationalisering_ontwikkelingssamenwerking'] = {}
                
                # Export en internationalisering subcategory
                if st.checkbox("Export en internationalisering", key="export_int"):
                    st.markdown("###### Export en internationalisering subcategorieën")
                    category_filters['export_internationalisering_ontwikkelingssamenwerking']['export_en_internationalisering'] = {
                        'export_krediet_verzekering_garantie': st.checkbox("Export krediet, verzekering en garantie", key="export_krediet"),
                        'internationalisering': st.checkbox("Internationalisering", key="export_inter"),
                        'promotionele_activiteiten': st.checkbox("Promotionele activiteiten", key="export_promo")
                    }
                
                # Other categories
                category_filters['export_internationalisering_ontwikkelingssamenwerking'].update({
                    'ontwikkelingssamenwerking': st.checkbox("Ontwikkelingssamenwerking", key="export_ontwikkeling"),
                    'stedenbanden_en_uitwisseling': st.checkbox("Stedenbanden en uitwisseling", key="export_stedenbanden")
                })

        with tabs[5]:  # Gezondheidszorg & Welzijn
            if st.checkbox("Gezondheidszorg & Welzijn"):
                st.markdown("##### Gezondheidszorg & Welzijn subcategorieën")
                category_filters['gezondheidszorg_welzijn'] = {}
                
                # Gezondheidszorg main category
                if st.checkbox("Gezondheidszorg"):
                    st.markdown("###### Gezondheidszorg subcategorieën")
                    category_filters['gezondheidszorg_welzijn']['gezondheidszorg'] = {
                        'geestelijke_gezondheidszorg': st.checkbox("Geestelijke gezondheidszorg", key="gz_ggz"),
                        'gehandicaptenzorg': st.checkbox("Gehandicaptenzorg", key="gz_gehandicapt"),
                        'gezondheidsbescherming': st.checkbox("Gezondheidsbescherming", key="gz_bescherming"),
                        'gezondheidszorg_ziekenhuizen': st.checkbox("Gezondheidszorg ziekenhuizen", key="gz_ziekenhuis"),
                        'zorgvoorziening': st.checkbox("Zorgvoorziening", key="gz_voorziening")
                    }
                
                # Welzijn main category
                if st.checkbox("Welzijn"):
                    st.markdown("###### Welzijn subcategorieën")
                    category_filters['gezondheidszorg_welzijn']['welzijn'] = {
                        'armoedebestrijding': st.checkbox("Armoedebestrijding", key="welzijn_armoede"),
                        'buurtwerk': st.checkbox("Buurtwerk", key="welzijn_buurt"),
                        'dierenwelzijn': st.checkbox("Dierenwelzijn", key="welzijn_dieren"),
                        'emancipatie': st.checkbox("Emancipatie", key="welzijn_emancipatie"),
                        'gehandicapten': st.checkbox("Gehandicapten", key="welzijn_gehandicapt"),
                        'integratie_nieuwkomers': st.checkbox("Integratie nieuwkomers", key="welzijn_integratie"),
                        'jeugd_jongeren': st.checkbox("Jeugd en jongeren", key="welzijn_jeugd"),
                        'ouderen': st.checkbox("Ouderen", key="welzijn_ouderen"),
                        'wonen_zorg_domotica': st.checkbox("Wonen, zorg en domotica", key="welzijn_wonen")
                    }

        with tabs[6]:  # ICT
            if st.checkbox("ICT"):
                st.markdown("##### ICT subcategorieën")
                category_filters['ict'] = {
                    'hardware': st.checkbox("Hardware", key="ict_hardware"),
                    'infrastructuur': st.checkbox("Infrastructuur", key="ict_infra"),
                    'internet_toepassingen': st.checkbox("Internet toepassingen", key="ict_internet"),
                    'software': st.checkbox("Software", key="ict_software"),
                    'telecommunicatie': st.checkbox("Telecommunicatie", key="ict_telecom")
                }

        with tabs[7]:  # Landbouw & Visserij
            if st.checkbox("Landbouw & Visserij"):
                st.markdown("##### Landbouw & Visserij subcategorieën")
                category_filters['landbouw_visserij'] = {
                    'landbouw': st.checkbox("Landbouw", key="landbouw_main"),
                    'visserij': st.checkbox("Visserij", key="visserij_main")
                }

        with tabs[8]:  # Levensbeschouwing
            if st.checkbox("Levensbeschouwing"):
                st.markdown("##### Levensbeschouwing subcategorieën")
                category_filters['levensbeschouwing'] = {
                    'levensbeschouwing': st.checkbox("Levensbeschouwing", key="levensbeschouwing_main")
                }

        with tabs[9]:  # Milieu
            if st.checkbox("Milieu"):
                st.markdown("##### Milieu subcategorieën")
                category_filters['milieu'] = {
                    'afvalverwerking': st.checkbox("Afvalverwerking", key="milieu_afval"),
                    'bodemverontreiniging': st.checkbox("Bodemverontreiniging", key="milieu_bodem"),
                    'luchtkwaliteit': st.checkbox("Luchtkwaliteit", key="milieu_lucht"),
                    'milieueducatie': st.checkbox("Milieueducatie", key="milieu_educatie"),
                    'vervuilingsreductie': st.checkbox("Vervuilingsreductie", key="milieu_vervuiling")
                }

        with tabs[10]:  # Natuurbeheer
            if st.checkbox("Natuurbeheer"):
                st.markdown("##### Natuurbeheer subcategorieën")
                category_filters['natuurbeheer'] = {
                    'aankoop_inrichting': st.checkbox("Aankoop en inrichting"),
                    'beheer_onderhoud': st.checkbox("Beheer en onderhoud"),
                    'inrichting_functiewijziging': st.checkbox("Inrichting en functiewijziging"),
                    'soortenbescherming': st.checkbox("Soortenbescherming")
                }

        with tabs[11]:  # Ondersteunend Bedrijfsleven
            if st.checkbox("Ondersteunend Bedrijfsleven"):
                st.markdown("##### Ondersteunend Bedrijfsleven subcategorieën")
                category_filters['ondersteunend_bedrijfsleven'] = {
                    'ondersteunend_bedrijfsleven': st.checkbox("Ondersteunend Bedrijfsleven")
                }

        with tabs[12]:  # Onderwijs
            if st.checkbox("Onderwijs"):
                st.markdown("##### Onderwijs subcategorieën")
                category_filters['onderwijs'] = {
                    'hoger_onderwijs': st.checkbox("Hoger onderwijs"),
                    'middelbaar_beroepsonderwijs': st.checkbox("MBO"),
                    'primair_onderwijs': st.checkbox("Primair onderwijs"),
                    'voortgezet_onderwijs': st.checkbox("Voortgezet onderwijs")
                }

        with tabs[13]:  # Onderzoek
            if st.checkbox("Onderzoek"):
                st.markdown("##### Onderzoek subcategorieën")
                category_filters['onderzoek'] = {
                    'kennisoverdracht': st.checkbox("Kennisoverdracht"),
                    'overige_regelingen': st.checkbox("Overige regelingen")
                }
                if st.checkbox("Innovatie", key="onderzoek_innovatie"):
                    st.markdown("###### Innovatie subcategorieën")
                    category_filters['onderzoek']['innovatie'] = {
                        'bedrijfsparticipatie': st.checkbox("Bedrijfsparticipatie", key="onderzoek_innovatie_bedrijfsparticipatie"),
                        'procesinnovatie': st.checkbox("Procesinnovatie", key="onderzoek_innovatie_procesinnovatie"),
                        'productinnovatie': st.checkbox("Productinnovatie", key="onderzoek_innovatie_productinnovatie"),
                        'software': st.checkbox("Software", key="onderzoek_innovatie_software"),
                        'sociale_innovatie': st.checkbox("Sociale innovatie", key="onderzoek_innovatie_sociale")
                    }
                if st.checkbox("Wetenschap", key="onderzoek_wetenschap"):
                    st.markdown("###### Wetenschap subcategorieën")
                    category_filters['onderzoek']['wetenschap'] = {
                        'formele_wetenschappen': st.checkbox("Formele wetenschappen"),
                        'fundamenteel_onderzoek': st.checkbox("Fundamenteel onderzoek"),
                        'geesteswetenschappen': st.checkbox("Geesteswetenschappen"),
                        'geneeskunde': st.checkbox("Geneeskunde"),
                        'natuurwetenschappen': st.checkbox("Natuurwetenschappen"),
                        'sociale_wetenschappen': st.checkbox("Sociale wetenschappen"),
                        'toegepast_onderzoek': st.checkbox("Toegepast onderzoek")
                    }

        with tabs[14]:  # Regionale Ontwikkeling
            if st.checkbox("Regionale Ontwikkeling"):
                st.markdown("##### Regionale Ontwikkeling subcategorieën")
                category_filters['regionale_ontwikkeling'] = {
                    'bedrijventerreinen': st.checkbox("Bedrijventerreinen"),
                    'infrastructuur': st.checkbox("Infrastructuur"),
                    'plattelandsontwikkeling': st.checkbox("Plattelandsontwikkeling"),
                    'stedelijke_vernieuwing': st.checkbox("Stedelijke vernieuwing")
                }

        with tabs[15]:  # Sport, Recreatie & Toerisme
            if st.checkbox("Sport, Recreatie & Toerisme"):
                st.markdown("##### Sport, Recreatie & Toerisme subcategorieën")
                category_filters['sport_recreatie_toerisme'] = {
                    'recreatie_en_ontspanning': st.checkbox("Recreatie en ontspanning"),
                    'sport': {
                        'breedtesport': st.checkbox("Breedtesport"),
                        'gehandicaptensport': st.checkbox("Gehandicaptensport"),
                        'topsport': st.checkbox("Topsport")
                    },
                    'toerisme': st.checkbox("Toerisme")
                }
                if st.checkbox("Sport"):
                    st.markdown("###### Sport subcategorieën")
                    category_filters['sport_recreatie_toerisme']['sport'] = {
                        'breedtesport': st.checkbox("Breedtesport"),
                        'gehandicaptensport': st.checkbox("Gehandicaptensport"),
                        'topsport': st.checkbox("Topsport")
                    }

        with tabs[16]:  # Transport & Mobiliteit
            if st.checkbox("Transport & Mobiliteit"):
                st.markdown("##### Transport & Mobiliteit subcategorieën")
                category_filters['transport_mobiliteit'] = {
                    'lucht': st.checkbox("Lucht"),
                    'ruimtevaart': st.checkbox("Ruimtevaart"),
                    'spoor': st.checkbox("Spoor"),
                    'transport_en_brandstofbesparing': st.checkbox("Transport en brandstofbesparing"),
                    'water': st.checkbox("Water"),
                    'weg': st.checkbox("Weg")
                }

        with tabs[17]:  # Veiligheid
            if st.checkbox("Veiligheid"):
                st.markdown("##### Veiligheid subcategorieën")
                category_filters['veiligheid'] = {
                    'brandweer_rampenbestrijding': st.checkbox("Brandweer en rampenbestrijding"),
                    'criminaliteit_veiligheid': st.checkbox("Criminaliteit en veiligheid"),
                    'verkeersveiligheid': st.checkbox("Verkeersveiligheid"),
                    'waterkeringen': st.checkbox("Waterkeringen")
                }

    # Main content
    st.title("🔍 Subsidie Zoeker")
    st.markdown("""
    Zoek naar beschikbare subsidies door uw zoekopdracht hieronder in te voeren.
    Bijvoorbeeld: *"Ik zoek naar subsidies voor duurzame energie in Gelderland"*
    """)
    
    # Input section
    user_input = st.text_area(
        "Beschrijf waar u naar op zoek bent:",
        height=100,
        placeholder="Bijvoorbeeld: Ik zoek naar innovatie subsidies voor het MKB in de provincie Overijssel..."
    )
    
    # Search button
    if st.button("Zoeken", type="primary"):
        if user_input:
            with st.spinner('Bezig met zoeken...'):
                try:
                    # Convert checkbox values to proper nested structure
                    formatted_categories = {}
                    for main_category, subcategories in category_filters.items():
                        if isinstance(subcategories, dict):
                            # Handle nested subcategories
                            formatted_subcategories = {}
                            for sub_key, sub_value in subcategories.items():
                                if isinstance(sub_value, dict):
                                    # Handle deeply nested subcategories
                                    formatted_subcategories[sub_key] = {
                                        k: v if v else None 
                                        for k, v in sub_value.items()
                                    }
                                else:
                                    formatted_subcategories[sub_key] = sub_value if sub_value else None
                            formatted_categories[main_category] = formatted_subcategories
                        else:
                            formatted_categories[main_category] = subcategories if subcategories else None

                    logger.debug(f"Formatted categories:\n\n{formatted_categories}")                   
                    # Retrieve both sets of results
                    results, nodes_embed = retrieve_subsidies(
                        user_input,
                        include_national=include_national,
                        regions=selected_regions,
                        categories=formatted_categories,
                        status=selected_status
                    )
                    
                    results2, nodes_embed2 = retrieve_subsidies(
                        user_input,
                        include_national=include_national,
                        regions=selected_regions,
                        categories=formatted_categories,
                        status=selected_status,
                        collection_name="vindsub_subsidies_2024_v1_openai",
                        embed_model="openai"
                    )
                    
                    # Create two columns for side-by-side comparison
                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.subheader(f"🎯 Resultaten Set 1: Top {len(results)}")
                        for node in results:
                            display_node(node)
                            
                    with col_right:
                        st.subheader(f"🎯 Resultaten Set 2: Top {len(results2)}")
                        for node in results2:
                            display_node(node)
                        
                except Exception as e:
                    error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
                    logger.error(error_msg)  # This will print to terminal
                    st.error(f"Er is een fout opgetreden: {str(e)}")  # This will show in UI
        else:
            st.warning("Voer eerst een zoekopdracht in.")

if __name__ == "__main__":
    main()
