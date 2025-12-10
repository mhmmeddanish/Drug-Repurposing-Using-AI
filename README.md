# Drug Repurposing Using AI  
### An AI-powered system to discover new therapeutic uses for existing drugs using vector embeddings, similarity search, and an interactive Streamlit interface.

---

## Project Overview

Drug discovery is one of the most expensive and time-consuming processes in modern medicine, often requiring more than a decade and billions of dollars.  
This project demonstrates how AI and vector databases can accelerate drug repurposing by enabling:

- Identification of drug candidates for diseases  
- Discovery of new therapeutic uses for existing drugs  
- Analysis of molecular and pharmacological properties  
- Embedding-based similarity search between drugs and diseases  
- Interactive natural-language conversation through an integrated AI assistant  

All packaged in a streamlined and user-friendly Streamlit application.

---

## Key Features

### Smart Search Module
- Search for drugs relevant to a disease  
- Search for diseases associated with a drug  
- Identify similar drugs through vector similarity  
- Fuzzy and partial text matching  
- Confidence scoring and ranking  
- PubChem linking  
- Interactive bar charts using Plotly  

---

## AI Assistant

A conversational assistant capable of answering:

- “What drugs help with Alzheimer’s?”  
- “What is diabetes?”  
- “What can Metformin be used for?”  
- “Explain drug repurposing”  

It generates structured, biomedical explanations plus embedding-based drug recommendations.

---

## Analytics Dashboard
Includes visualizations for:
- Lipinski rule compliance  
- BBB permeability distribution  
- Molecular weight histograms  
- Drug-likeness and property summaries  

---

## Database Explorer
Browse:
- All drugs in the database  
- All diseases in the database  
Filter results using simple text queries.

---

## Tech Stack

### Libraries Used
- ChromaDB (vector DB)
- Streamlit (frontend UI)
- Pandas & NumPy (data processing)
- Plotly (visual analytics)
- RDKit (optional chemical property utilities)
- Custom SmartSearch module for retrieval logic

### Deployment Platforms
- Render  
- Streamlit Cloud  
- Local Execution  

---

## Installation

1. Clone the project:

    git clone https://github.com/your-username/Drug-Repurposing-Using-AI.git
    cd Drug-Repurposing-Using-AI

2. Install dependencies:

    pip install -r requirements.txt

3. Prepare the vector database (only needed once).  
   Run these scripts in order:

    python scripts/01_download_data.py  
    python scripts/02_collect_metadata.py  
    python scripts/03_enrich_metadata.py  
    python scripts/04_create_embeddings.py  
    python scripts/05_setup_vector_db.py

This will create the folder `data/vector_db`, which the Streamlit app uses.

---

## Run the App

To launch the interface locally:

    streamlit run app.py

Make sure `data/vector_db` exists before running.

---

## What the App Can Do

### Smart Search
- Find drugs related to a disease  
- Find diseases related to a drug  
- Find drugs that are similar to another drug  
- View confidence scores, molecular weight, Lipinski results, BBB permeability, and more  

### AI Assistant
- Ask basic questions about diseases or drugs  
- Get explanations for drug repurposing  
- Automatically receive drug suggestions based on your query  

### Analytics
- View distributions for molecular weight, BBB permeability, and Lipinski rule outcomes  
- Explore general statistics of the drug dataset  

### Database Explorer
- Browse all drugs and diseases  
- Filter them using simple text search  

---

## Deployment (Render)

Build command:

    pip install -r requirements.txt

Start command:

    streamlit run app.py --server.port $PORT --server.address 0.0.0.0

Make sure the `data/vector_db` folder is included in the repository so the database loads correctly when deployed.

---

## Notes

- This project is for learning and research purposes, not medical use.  
- The suggestions are based on vector similarity, not clinical validation.  
- The quality of results depends heavily on the embedding model and data used.

---
