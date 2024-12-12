import streamlit as st
from agent.retrievers.retriever_baseline import retrieve_subsidies


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
    
    # Header
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
                    # Retrieve results
                    results, nodes_embed = retrieve_subsidies(user_input)
                    
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
