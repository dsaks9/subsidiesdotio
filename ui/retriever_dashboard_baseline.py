import streamlit as st
from agent.retrievers.retriever_baseline import retrieve_subsidies
from agent.tools.subsidy_report_parameters import REGIONS
from agent.tools.tool_query_subsidies import CategorieSelectie


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
                    'activering_en_instroom': st.checkbox("Activering en instroom"),
                    'gesubsidieerd_werk': st.checkbox("Gesubsidieerd werk"),
                    'integratie_en_reintegratie': st.checkbox("Integratie en reïntegratie"),
                    'leeftijdsbewust_beleid': st.checkbox("Leeftijdsbewust beleid"),
                    'werknemersopleiding': st.checkbox("Werknemersopleiding"),
                    'stages_werkleertrajecten': st.checkbox("Stages en werkleertrajecten")
                }
                
                if st.checkbox("Uitstroom verbetering", key="arbeidsmarkt_uitstroom"):
                    st.markdown("##### Uitstroom verbetering subcategorieën")
                    category_filters['arbeidsmarkt']['uitstroom_verbetering'] = {
                        'werkervaring_evc': st.checkbox("Werkervaring en EVC"),
                        'loopbaanbegeleiding': st.checkbox("Loopbaanbegeleiding"),
                        'uitstroom_verbetering': st.checkbox("Algemene uitstroom verbetering"),
                        'loonkosten': st.checkbox("Loonkosten"),
                        'vacaturevervulling': st.checkbox("Vacaturevervulling")
                    }

        with tabs[1]:  # Bouw
            if st.checkbox("Bouw"):
                st.markdown("##### Bouw subcategorieën")
                category_filters['bouw'] = {
                    'afwerking': st.checkbox("Afwerking"),
                    'burgerlijke_utiliteitsbouw': st.checkbox("Burgerlijke utiliteitsbouw"),
                    'civiele_techniek': st.checkbox("Civiele techniek"),
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
                category_filters['duurzame_energie'] = {
                    'energiebesparing_isolatie': st.checkbox("Energiebesparing en isolatie"),
                    'fossiele_energie': st.checkbox("Fossiele energie"),
                    'kernenergie': st.checkbox("Kernenergie")
                }

        with tabs[4]:  # Export, Internationalisering & Ontwikkelingssamenwerking
            if st.checkbox("Export, Internationalisering & Ontwikkelingssamenwerking"):
                st.markdown("##### Export, Internationalisering & Ontwikkelingssamenwerking subcategorieën")
                category_filters['export_internationalisering_ontwikkelingssamenwerking'] = {
                    'export_internationalisering': st.checkbox("Export en internationalisering"),
                    'ontwikkelingssamenwerking': st.checkbox("Ontwikkelingssamenwerking")
                }

        with tabs[5]:  # Gezondheidszorg & Welzijn
            if st.checkbox("Gezondheidszorg & Welzijn"):
                st.markdown("##### Gezondheidszorg & Welzijn subcategorieën")
                category_filters['gezondheidszorg_welzijn'] = {
                    'gezondheidszorg': st.checkbox("Gezondheidszorg"),
                    'welzijn': st.checkbox("Welzijn")
                }

        with tabs[6]:  # ICT
            if st.checkbox("ICT"):
                st.markdown("##### ICT subcategorieën")
                category_filters['ict'] = {
                    'hardware': st.checkbox("Hardware"),
                    'infrastructuur': st.checkbox("Infrastructuur"),
                    'internet_toepassingen': st.checkbox("Internet toepassingen"),
                    'software': st.checkbox("Software"),
                    'telecommunicatie': st.checkbox("Telecommunicatie")
                }

        with tabs[7]:  # Landbouw & Visserij
            if st.checkbox("Landbouw & Visserij"):
                st.markdown("##### Landbouw & Visserij subcategorieën")
                category_filters['landbouw_visserij'] = {
                    'landbouw': st.checkbox("Landbouw"),
                    'visserij': st.checkbox("Visserij")
                }

        with tabs[8]:  # Levensbeschouwing
            if st.checkbox("Levensbeschouwing"):
                st.markdown("##### Levensbeschouwing subcategorieën")
                category_filters['levensbeschouwing'] = {
                    'levensbeschouwing': st.checkbox("Levensbeschouwing")
                }

        with tabs[9]:  # Milieu
            if st.checkbox("Milieu"):
                st.markdown("##### Milieu subcategorieën")
                category_filters['milieu'] = {
                    'afvalverwerking': st.checkbox("Afvalverwerking"),
                    'bodemverontreiniging': st.checkbox("Bodemverontreiniging"),
                    'luchtkwaliteit': st.checkbox("Luchtkwaliteit"),
                    'milieueducatie': st.checkbox("Milieueducatie"),
                    'vervuilingsreductie': st.checkbox("Vervuilingsreductie")
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
                    st.markdown("##### Innovatie subcategorieën")
                    category_filters['onderzoek']['innovatie'] = {
                        'bedrijfsparticipatie': st.checkbox("Bedrijfsparticipatie", key="onderzoek_innovatie_bedrijfsparticipatie"),
                        'procesinnovatie': st.checkbox("Procesinnovatie", key="onderzoek_innovatie_procesinnovatie"),
                        'productinnovatie': st.checkbox("Productinnovatie", key="onderzoek_innovatie_productinnovatie"),
                        'software': st.checkbox("Software", key="onderzoek_innovatie_software"),
                        'sociale_innovatie': st.checkbox("Sociale innovatie", key="onderzoek_innovatie_sociale")
                    }
                if st.checkbox("Wetenschap", key="onderzoek_wetenschap"):
                    st.markdown("##### Wetenschap subcategorieën")
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
                    'sport_recreatie_toerisme': st.checkbox("Sport, Recreatie & Toerisme")
                }

        with tabs[16]:  # Transport & Mobiliteit
            if st.checkbox("Transport & Mobiliteit"):
                st.markdown("##### Transport & Mobiliteit subcategorieën")
                category_filters['transport_mobiliteit'] = {
                    'transport_mobiliteit': st.checkbox("Transport & Mobiliteit")
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

                    # Retrieve results with formatted filters
                    results, nodes_embed = retrieve_subsidies(
                        user_input,
                        include_national=include_national,
                        regions=selected_regions,
                        categories=formatted_categories,
                        status=selected_status
                    )
                    
                    # Display results
                    st.subheader(f"🎯 Gevonden resultaten: {len(results)}")
                    
                    # Display each result
                    for node in results:
                        display_node(node)
                        
                except Exception as e:
                    st.error(f"Er is een fout opgetreden: {str(e)}")
        else:
            st.warning("Voer eerst een zoekopdracht in.")

if __name__ == "__main__":
    main()
