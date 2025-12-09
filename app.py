"""
🧬 Drug Repurposing AI - Streamlit Interface
Interactive search with AI chatbot assistance
"""

import streamlit as st
import chromadb
from chromadb.config import Settings
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).parent.absolute()

# Add scripts to path
sys.path.append(str(PROJECT_ROOT / 'scripts'))

# Import after adding to path
try:
    from search_utils import SmartSearch
except ImportError:
    st.error("❌ Cannot import search_utils. Make sure scripts/search_utils.py exists!")
    st.stop()

# Page config
st.set_page_config(
    page_title="Drug Repurposing AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .stAlert {
        border-radius: 10px;
    }
    .drug-card {
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
    }
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = None

@st.cache_resource
def load_database():
    """Load ChromaDB database (cached)"""
    # Use absolute path
    db_path = PROJECT_ROOT / "data" / "vector_db"
    
    if not db_path.exists():
        st.error(f"❌ Database not found!")
        st.error(f"Expected location: `{db_path}`")
        
        st.info("### 🚀 Setup Steps:")
        st.code("""
            # Run these commands from your project root:
            cd """ + str(PROJECT_ROOT) + """

            python scripts/01_download_data.py
            python scripts/02_collect_metadata.py
            python scripts/03_enrich_metadata.py
            python scripts/04_create_embeddings.py
            python scripts/05_setup_vector_db.py
                    """, language="bash")
        
        st.stop()
    
    try:
        client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        drug_collection = client.get_collection("drugs")
        disease_collection = client.get_collection("diseases")
        
        smart_search = SmartSearch(drug_collection, disease_collection)
        
        return drug_collection, disease_collection, smart_search
    
    except Exception as e:
        st.error(f"❌ Error loading database: {str(e)}")
        st.stop()
    # @st.cache_resource
    # def load_database():
    #     """Load ChromaDB database (cached)"""
    #     db_path = PROJECT_ROOT / "data" / "vector_db"
        
    #     if not db_path.exists():
    #         st.error(f"❌ Database not found!")
    #         st.error(f"Expected location: `{db_path}`")
    #         ...
    #         st.stop()
        
    #     try:
    #         client = chromadb.PersistentClient(
    #             path=str(db_path),
    #             settings=Settings(anonymized_telemetry=False)
    #         )
    
    #         # 👇 TEMP: show what collections exist
    #         collections = [c.name for c in client.list_collections()]
    #         st.write("Available collections:", collections)
    
    #         drug_collection = client.get_collection("drugs")
    #         disease_collection = client.get_collection("diseases")
    
    #         smart_search = SmartSearch(drug_collection, disease_collection)
    #         return drug_collection, disease_collection, smart_search
    
    #     except Exception as e:
    #         import traceback
    #         st.error(f"❌ Error loading database: {repr(e)}")
    #         st.error("Stack trace:")
    #         st.code(traceback.format_exc())
    #         st.stop()

# ⭐ MOVE THIS FUNCTION HERE - BEFORE IT'S USED ⭐
def generate_smart_response(user_input, smart_search, drug_collection, disease_collection):
    """Generate intelligent responses based on user input"""
    import re
    
    user_lower = user_input.lower().strip()
    
    # Remove common filler words
    filler_words = ['what', 'is', 'a', 'an', 'the', 'about', 'tell', 'me', 'can', 'you', 'help', 'with', 'for']
    words = user_lower.split()
    clean_words = [w for w in words if w not in filler_words]
    clean_query = ' '.join(clean_words)
    
    # Enhanced disease keywords with fuzzy matching
    disease_patterns = {
        'alzheimer': {
            'keywords': ['alzheimer', 'alzhimer', 'alziehmer', 'alzheimers', 'dementia', 'memory loss', 'cognitive decline'],
            'search_query': "Alzheimer's disease neurodegeneration cognitive decline dementia brain memory",
            'display_name': "Alzheimer's disease"
        },
        'diabetes': {
            'keywords': ['diabetes', 'diabetic', 'diabetis', 'sugar', 'insulin', 'glucose'],
            'search_query': "diabetes mellitus insulin glucose blood sugar metabolic",
            'display_name': "Diabetes"
        },
        'cancer': {
            'keywords': ['cancer', 'tumor', 'carcinoma', 'malignant', 'oncology'],
            'search_query': "cancer carcinoma tumor malignant neoplasm oncology",
            'display_name': "Cancer"
        },
        'heart': {
            'keywords': ['heart', 'cardiac', 'cardiovascular', 'coronary', 'myocardial'],
            'search_query': "heart disease cardiovascular coronary cardiac myocardial",
            'display_name': "Heart Disease"
        },
        'parkinson': {
            'keywords': ['parkinson', 'parkinsons', 'tremor', 'movement disorder'],
            'search_query': "Parkinson's disease movement disorder tremor dopamine",
            'display_name': "Parkinson's disease"
        },
        'depression': {
            'keywords': ['depression', 'depressed', 'sad', 'mood disorder', 'mental health'],
            'search_query': "depression mental health mood disorder psychiatric",
            'display_name': "Depression"
        },
        'hypertension': {
            'keywords': ['hypertension', 'high blood pressure', 'blood pressure'],
            'search_query': "hypertension high blood pressure cardiovascular",
            'display_name': "Hypertension"
        },
        'asthma': {
            'keywords': ['asthma', 'breathing', 'respiratory', 'airway'],
            'search_query': "asthma respiratory breathing airway inflammation",
            'display_name': "Asthma"
        },
        'arthritis': {
            'keywords': ['arthritis', 'joint pain', 'rheumatoid', 'osteoarthritis'],
            'search_query': "arthritis joint inflammation pain rheumatoid",
            'display_name': "Arthritis"
        }
    }
    
    if any(phrase in user_lower for phrase in ['what is', 'what are', 'tell me about', 'explain', 'define']):
        for disease_key, disease_info in disease_patterns.items():
            for keyword in disease_info['keywords']:
                if keyword in user_lower:
                    disease_name = disease_info['display_name']
                    
                    descriptions = {
                        "Alzheimer's disease": "**Alzheimer's disease** is a progressive neurodegenerative disorder that affects memory, thinking, and behavior. It's the most common cause of dementia.",
                        "Diabetes": "**Diabetes** is a metabolic disorder characterized by high blood sugar levels. Type 2 diabetes involves insulin resistance.",
                        "Cancer": "**Cancer** is a group of diseases involving abnormal cell growth with the potential to invade or spread to other parts of the body.",
                        "Heart Disease": "**Heart disease** refers to conditions that affect the heart, including coronary artery disease, heart attacks, and heart failure.",
                        "Parkinson's disease": "**Parkinson's disease** is a progressive nervous system disorder that affects movement, causing tremors, stiffness, and balance problems.",
                        "Depression": "**Depression** is a mental health disorder characterized by persistent feelings of sadness, loss of interest, and low energy.",
                        "Hypertension": "**Hypertension** (high blood pressure) is a condition where the force of blood against artery walls is consistently too high.",
                        "Asthma": "**Asthma** is a chronic respiratory condition causing inflammation and narrowing of airways, leading to breathing difficulties.",
                        "Arthritis": "**Arthritis** is inflammation of the joints, causing pain and stiffness. Common types include osteoarthritis and rheumatoid arthritis."
                    }
                    
                    response = descriptions.get(disease_name, f"**{disease_name}** is a medical condition.")
                    response += f"\n\n**Potential drug candidates for {disease_name}:**\n\n"
                    
                    results = smart_search.search_drugs_fuzzy(disease_info['search_query'], top_k=5)
                    
                    for r in results[:5]:
                        response += f"**{r['rank']}. {r['drug_name']}** - {r['confidence']}% confidence\n"
                    
                    response += f"\n💡 Use the **🔍 Smart Search** tab to explore more treatment options for {disease_name}!"
                    return response
    
    for disease_key, disease_info in disease_patterns.items():
        for keyword in disease_info['keywords']:
            if keyword in clean_query or keyword in user_lower:
                results = smart_search.search_drugs_fuzzy(disease_info['search_query'], top_k=5)
                
                disease_name = disease_info['display_name']
                response = f"**Drug candidates for {disease_name}:**\n\n"
                
                for r in results[:5]:
                    response += f"**{r['rank']}. {r['drug_name']}** - Confidence: {r['confidence']}%\n"
                    
                    # Add properties
                    mw = r['molecular_weight']
                    if isinstance(mw, (int, float)) and mw > 0:
                        response += f"   • Molecular Weight: {mw:.2f}\n"
                    response += f"   • Drug-like: {'✅' if r['passes_lipinski'] else '❌'}\n"
                    response += f"   • BBB Permeable: {'✅' if r['bbb_permeable'] else '❌'}\n\n"
                
                response += f"\n💡 Try the **🔍 Smart Search** tab for detailed results with charts!"
                return response
    
    # Check if user is asking about a specific drug
    drug_names_common = [
        'aspirin', 'ibuprofen', 'metformin', 'paracetamol', 'acetaminophen',
        'insulin', 'atorvastatin', 'lisinopril', 'amlodipine', 'metoprolol',
        'omeprazole', 'simvastatin', 'losartan', 'gabapentin', 'sertraline'
    ]
    
    for drug in drug_names_common:
        if drug in user_lower:
            # Find the drug (case-insensitive)
            exact_match, suggestions = smart_search.find_drug(drug)
            
            if exact_match:
                # Get potential applications
                drug_result = drug_collection.get(
                    where={"drug_name": exact_match},
                    include=["embeddings"]
                )
                
                if drug_result['ids'] and len(drug_result['ids']) > 0:
                    results = disease_collection.query(
                        query_embeddings=[drug_result['embeddings'][0]],
                        n_results=5
                    )
                    
                    response = f"**Potential uses for {exact_match}:**\n\n"
                    
                    for i, (metadata, distance) in enumerate(zip(
                        results['metadatas'][0],
                        results['distances'][0]
                    ), 1):
                        confidence = (1 - distance) * 100
                        response += f"{i}. **{metadata['disease_name']}** - {confidence:.1f}% confidence\n"
                    
                    response += "\n💡 Use the **🔍 Smart Search** tab to explore more!"
                    return response
    
    # Check for general questions about the system
    if any(word in user_lower for word in ['how', 'explain', 'tell']):
        if 'drug repurposing' in user_lower or 'repurpose' in user_lower or 'work' in user_lower:
            return """**About Drug Repurposing:**

Drug repurposing (or repositioning) is finding new therapeutic uses for existing drugs. 

**Why it matters:**
- ⚡ **Faster** - Years instead of decades
- 💰 **Cheaper** - Millions vs billions of dollars  
- ✅ **Safer** - Drugs already passed safety trials
- 🤖 **AI-powered** - Finds hidden connections in data

**How this system works:**
1. Drugs and diseases are converted to AI embeddings (vectors)
2. Similar vectors = similar biological properties
3. Search finds the best drug-disease matches
4. Confidence scores show how strong the match is

**Try it yourself:**
- Type "diabetes" or "alzheimer" to find drug candidates
- Type a drug name to find new uses
- Use the 🔍 Smart Search tab for detailed results!"""
        
        elif 'use' in user_lower or 'help' in user_lower:
            return """**How to use this system:**

**🔍 Smart Search Tab:**
- Find drugs for diseases
- Find diseases for drugs  
- Find similar drugs
- Case-insensitive & fuzzy matching!

**💬 AI Assistant (here!):**
- Ask about diseases: *"What is Alzheimer's?"*
- Ask about drugs: *"What can Metformin treat?"*
- Get drug suggestions: *"Drugs for diabetes"*

**📊 Analytics Tab:**
- View database statistics
- See drug property distributions

**📚 Database Explorer:**
- Browse all drugs and diseases

**Example questions:**
- "What drugs help with Alzheimer's?"
- "What is diabetes?"
- "What can Aspirin be used for?"
- "Drugs for heart disease"

Try asking about any disease!"""
    
    # If no specific pattern matched, check if it's just a disease name
    if len(clean_words) <= 3:  # Short query, probably just a disease name
        # Try searching for it as a disease
        for disease_key, disease_info in disease_patterns.items():
            for keyword in disease_info['keywords']:
                # More lenient matching for short queries
                if keyword in user_lower or user_lower in keyword:
                    results = smart_search.search_drugs_fuzzy(disease_info['search_query'], top_k=5)
                    
                    disease_name = disease_info['display_name']
                    response = f"**Searching for drugs to treat {disease_name}...**\n\n"
                    
                    for r in results[:5]:
                        response += f"**{r['rank']}. {r['drug_name']}** - {r['confidence']}% confidence\n"
                    
                    response += f"\n💡 Want to know more about {disease_name}? Ask: *'What is {disease_name}?'*"
                    return response
    
    # Default response with helpful examples
    return """I'm here to help with drug repurposing! 🤖

**I can answer:**
- "What drugs treat Alzheimer's?" 
- "What is diabetes?"
- "What can Metformin be used for?"
- "Drugs for heart disease"
- "Tell me about drug repurposing"

**Or just type:**
- Disease name: *"alzheimer"*, *"cancer"*, *"diabetes"*
- Drug name: *"aspirin"*, *"metformin"*

**Pro tip:** The **🔍 Smart Search** tab gives you detailed results with molecular properties and confidence scores!

Try asking about a disease or drug!"""
# Load database
drug_collection, disease_collection, smart_search = load_database()

# Header
st.markdown('<h1 class="main-header">🧬 Drug Repurposing AI</h1>', unsafe_allow_html=True)
st.markdown("### Discover new therapeutic uses for existing drugs using AI")

# Sidebar
with st.sidebar:
    # st.image("https://www.clipartmax.com/middle/m2i8d3m2i8Z5H7N4_repurposing-drugs-icon-recycling-symbol", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Choose a feature:",
        ["🔍 Smart Search", "💬 AI Assistant", "📊 Analytics", "📚 Database Explorer"]
    )
    
    st.markdown("---")
    
    # Stats
    drug_count = drug_collection.count()
    disease_count = disease_collection.count()
    
    st.metric("Total Drugs", drug_count)
    st.metric("Total Diseases", disease_count)
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Tips")
    st.info("""
    - Search is case-insensitive!
    - Type partial names (e.g., "alzheim")
    - Ask the AI assistant anything!
    """)

# Page: Smart Search
if page == "🔍 Smart Search":
    st.header("🔍 Intelligent Drug Search")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_type = st.radio(
            "What do you want to find?",
            ["💊 Drugs for a Disease", "🦠 Diseases for a Drug", "🔄 Similar Drugs"],
            horizontal=True
        )
    
    with col2:
        top_k = st.slider("Number of results", 5, 20, 10)
    
    st.markdown("---")
    
    # Search interface
    if search_type == "💊 Drugs for a Disease":
        query = st.text_input(
            "🔎 Enter disease name or description:",
            placeholder="e.g., alzheimer, diabetes, cancer, heart disease...",
            key="disease_search"
        )
        
        if st.button("🚀 Search", type="primary", use_container_width=True):
            if query:
                with st.spinner("🧠 AI is analyzing..."):
                    # Natural language search - no exact match needed!
                    results = smart_search.search_drugs_fuzzy(query, top_k=top_k)
                    st.session_state.search_results = results
                    
                    if results:
                        st.success(f"✅ Found {len(results)} potential drug candidates!")
                        
                        # Display results
                        for result in results:
                            confidence = result['confidence']
                            
                            # Confidence color
                            if confidence >= 75:
                                conf_class = "confidence-high"
                                emoji = "🟢"
                            elif confidence >= 60:
                                conf_class = "confidence-medium"
                                emoji = "🟡"
                            else:
                                conf_class = "confidence-low"
                                emoji = "🔴"
                            
                            with st.expander(f"{emoji} {result['rank']}. {result['drug_name']} - {confidence}% confidence"):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Confidence Score", f"{confidence}%")
                                    st.caption(f"Rank: #{result['rank']}")
                                
                                with col2:
                                    mw = result['molecular_weight']
                                    mw_display = f"{mw:.2f}" if isinstance(mw, (int, float)) and mw > 0 else "N/A"
                                    st.metric("Molecular Weight", mw_display)
                                    st.caption(f"Clinical Trials: {result['clinical_trials']}")
                                
                                with col3:
                                    lipinski = "✅ Yes" if result['passes_lipinski'] else "❌ No"
                                    bbb = "✅ Yes" if result['bbb_permeable'] else "❌ No"
                                    st.metric("Drug-like", lipinski)
                                    st.caption(f"BBB Permeable: {bbb}")
                                
                                if result['pubchem_cid'] and result['pubchem_cid'] != "unknown":
                                    st.markdown(f"[🔗 View on PubChem](https://pubchem.ncbi.nlm.nih.gov/compound/{result['pubchem_cid']})")
                        
                        # Visualization
                        st.markdown("---")
                        st.subheader("📊 Confidence Distribution")
                        
                        df = pd.DataFrame(results)
                        fig = px.bar(
                            df.head(10),
                            x='drug_name',
                            y='confidence',
                            color='confidence',
                            color_continuous_scale='Viridis',
                            title='Top 10 Drug Candidates by Confidence'
                        )
                        fig.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No results found. Try a different query!")
            else:
                st.warning("⚠️ Please enter a search query!")
    
    elif search_type == "🦠 Diseases for a Drug":
        drug_query = st.text_input(
            "🔎 Enter drug name:",
            placeholder="e.g., aspirin, metformin, ibuprofen...",
            key="drug_search"
        )
        
        if st.button("🚀 Search", type="primary", use_container_width=True):
            if drug_query:
                with st.spinner("🔍 Searching..."):
                    # Find drug with fuzzy matching
                    exact_match, suggestions = smart_search.find_drug(drug_query)
                    
                    if exact_match:
                        # Get drug embedding
                        drug_result = drug_collection.get(
                            where={"drug_name": exact_match},
                            include=["embeddings"]
                        )
                        
                        if drug_result['ids'] and len(drug_result['ids']) > 0:
                            # Search diseases
                            results = disease_collection.query(
                                query_embeddings=[drug_result['embeddings'][0]],
                                n_results=top_k
                            )
                            
                            st.success(f"✅ Found {len(results['metadatas'][0])} potential applications for **{exact_match}**")
                            
                            for i, (metadata, distance) in enumerate(zip(
                                results['metadatas'][0],
                                results['distances'][0]
                            ), 1):
                                confidence = (1 - distance) * 100
                                
                                with st.expander(f"{i}. {metadata['disease_name']} - {confidence:.1f}% confidence"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.metric("Confidence", f"{confidence:.1f}%")
                                        st.caption(f"EFO ID: {metadata['efo_id']}")
                                    
                                    with col2:
                                        st.metric("Known Drugs", metadata['known_drugs_count'])
                                        st.caption(f"Associated Targets: {metadata['targets_count']}")
                    
                    elif suggestions:
                        st.warning(f"⚠️ Drug '{drug_query}' not found. Did you mean:")
                        for sug in suggestions:
                            st.write(f"- {sug}")
                    else:
                        st.error(f"❌ No drug found matching '{drug_query}'")
            else:
                st.warning("⚠️ Please enter a drug name!")
    
    else:  # Similar Drugs
        drug_query = st.text_input(
            "🔎 Enter drug name:",
            placeholder="e.g., aspirin, metformin...",
            key="similar_search"
        )
        
        if st.button("🚀 Find Similar", type="primary", use_container_width=True):
            if drug_query:
                with st.spinner("🔍 Searching..."):
                    exact_match, suggestions = smart_search.find_drug(drug_query)
                    
                    if exact_match:
                        drug_result = drug_collection.get(
                            where={"drug_name": exact_match},
                            include=["embeddings"]
                        )
                        
                        if drug_result['ids'] and len(drug_result['ids']) > 0:
                            results = drug_collection.query(
                                query_embeddings=[drug_result['embeddings'][0]],
                                n_results=top_k + 1
                            )
                            
                            st.success(f"✅ Drugs similar to **{exact_match}**:")
                            
                            # Skip first result (the drug itself)
                            for i, (metadata, distance) in enumerate(zip(
                                results['metadatas'][0][1:],
                                results['distances'][0][1:]
                            ), 1):
                                similarity = (1 - distance) * 100
                                
                                st.write(f"{i}. **{metadata['drug_name']}** - Similarity: {similarity:.1f}%")
                    
                    elif suggestions:
                        st.warning(f"⚠️ Drug '{drug_query}' not found. Did you mean:")
                        for sug in suggestions:
                            st.write(f"- {sug}")

# Page: AI Assistant
elif page == "💬 AI Assistant":
    st.header("💬 AI Drug Repurposing Assistant")
    st.markdown("Ask me anything about drugs, diseases, or drug repurposing!")
    
    # Simple chatbot without external APIs
    user_input = st.text_input("Ask a question:", placeholder="e.g., What drugs could help with Alzheimer's?")
    
    if st.button("Send", type="primary"):
        if user_input:
            # Add to chat history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })
            
            # Generate response using the function defined above
            response = generate_smart_response(user_input, smart_search, drug_collection, disease_collection)
            
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now()
            })
    
    # Display chat history
    st.markdown("---")
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            st.markdown(f"**🧑 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 AI Assistant:**")
            st.markdown(msg['content'])
        st.caption(msg['timestamp'].strftime("%H:%M:%S"))
        st.markdown("---")
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

# Page: Analytics
elif page == "📊 Analytics":
    st.header("📊 Database Analytics")
    
    # Get all drugs
    all_drugs = drug_collection.get(include=["metadatas"])
    drugs_df = pd.DataFrame(all_drugs['metadatas'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Drug-likeness distribution
        if 'passes_lipinski' in drugs_df.columns:
            lipinski_counts = drugs_df['passes_lipinski'].value_counts()
            fig = px.pie(
                values=lipinski_counts.values,
                names=['Passes Lipinski' if lipinski_counts.index[i] else 'Fails Lipinski' for i in range(len(lipinski_counts))],
                title='Drug-Likeness Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # BBB permeability
        if 'bbb_permeable' in drugs_df.columns:
            bbb_counts = drugs_df['bbb_permeable'].value_counts()
            fig = px.pie(
                values=bbb_counts.values,
                names=['BBB Permeable' if bbb_counts.index[i] else 'Not BBB Permeable' for i in range(len(bbb_counts))],
                title='Blood-Brain Barrier Permeability'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Molecular weight distribution
    if 'molecular_weight' in drugs_df.columns:
        drugs_df['molecular_weight'] = pd.to_numeric(drugs_df['molecular_weight'], errors='coerce')
        valid_mw = drugs_df[drugs_df['molecular_weight'] > 0]
        
        if len(valid_mw) > 0:
            fig = px.histogram(
                valid_mw,
                x='molecular_weight',
                nbins=30,
                title='Molecular Weight Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)

# Page: Database Explorer
else:
    st.header("📚 Database Explorer")
    
    tab1, tab2 = st.tabs(["💊 Drugs", "🦠 Diseases"])
    
    with tab1:
        st.subheader("All Drugs in Database")
        all_drugs = drug_collection.get(include=["metadatas"])
        drugs_list = [m.get('drug_name', 'Unknown') for m in all_drugs['metadatas']]
        
        # Search filter
        search_filter = st.text_input("🔍 Filter drugs:", placeholder="Type to filter...")
        
        if search_filter:
            filtered = [d for d in drugs_list if search_filter.lower() in d.lower()]
        else:
            filtered = drugs_list
        
        st.write(f"Showing {len(filtered)} of {len(drugs_list)} drugs")
        
        # Display in columns
        cols = st.columns(3)
        for i, drug in enumerate(sorted(filtered)):
            cols[i % 3].write(f"• {drug}")
    
    with tab2:
        st.subheader("All Diseases in Database")
        all_diseases = disease_collection.get(include=["metadatas"])
        disease_list = [m.get('disease_name', 'Unknown') for m in all_diseases['metadatas']]
        
        # Search filter
        search_filter = st.text_input("🔍 Filter diseases:", placeholder="Type to filter...", key="disease_filter")
        
        if search_filter:
            filtered = [d for d in disease_list if search_filter.lower() in d.lower()]
        else:
            filtered = disease_list
        
        st.write(f"Showing {len(filtered)} of {len(disease_list)} diseases")
        
        # Display in columns
        cols = st.columns(2)
        for i, disease in enumerate(sorted(filtered)):
            cols[i % 2].write(f"• {disease}")
