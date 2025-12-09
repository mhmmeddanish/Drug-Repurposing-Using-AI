"""
Utility functions for intelligent search
"""

from difflib import get_close_matches
import re

class SmartSearch:
    def __init__(self, drug_collection, disease_collection):
        self.drug_collection = drug_collection
        self.disease_collection = disease_collection
        
        # Cache all drug and disease names
        self._cache_names()
    
    def _cache_names(self):
        """Cache all drug and disease names for fuzzy matching"""
        # Get all drugs
        all_drugs = self.drug_collection.get(include=["metadatas"])
        self.drug_names = [m.get('drug_name', '') for m in all_drugs['metadatas']]
        self.drug_names_lower = {name.lower(): name for name in self.drug_names}
        
        # Get all diseases
        all_diseases = self.disease_collection.get(include=["metadatas"])
        self.disease_names = [m.get('disease_name', '') for m in all_diseases['metadatas']]
        self.disease_names_lower = {name.lower(): name for name in self.disease_names}
    
    def find_drug(self, query):
        """
        Find drug with fuzzy matching and case-insensitive search
        Returns: (exact_match, suggested_names)
        """
        query_lower = query.lower().strip()
        
        if query_lower in self.drug_names_lower:
            return self.drug_names_lower[query_lower], []
        
        for lower_name, actual_name in self.drug_names_lower.items():
            if query_lower in lower_name or lower_name in query_lower:
                return actual_name, []
        
        suggestions = get_close_matches(query_lower, self.drug_names_lower.keys(), n=5, cutoff=0.6)
        suggested_names = [self.drug_names_lower[s] for s in suggestions]
        
        return None, suggested_names
    
    def find_disease(self, query):
        """
        Find disease with fuzzy matching and case-insensitive search
        Returns: (exact_match, suggested_names)
        """
        query_lower = query.lower().strip()
        
        # Exact match (case-insensitive)
        if query_lower in self.disease_names_lower:
            return self.disease_names_lower[query_lower], []
        
        # Partial match
        for lower_name, actual_name in self.disease_names_lower.items():
            if query_lower in lower_name or lower_name in query_lower:
                return actual_name, []
        
        # Fuzzy match
        suggestions = get_close_matches(query_lower, self.disease_names_lower.keys(), n=5, cutoff=0.6)
        suggested_names = [self.disease_names_lower[s] for s in suggestions]
        
        return None, suggested_names
    
    def search_drugs_fuzzy(self, disease_query, top_k=10):
        """
        Search for drugs using natural language query
        No exact disease name needed!
        """
        results = self.drug_collection.query(
            query_texts=[disease_query],
            n_results=top_k
        )
        
        candidates = []
        for i, (metadata, distance) in enumerate(zip(
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            similarity = (1 - distance) * 100
            
            candidates.append({
                'rank': i,
                'drug_name': metadata.get('drug_name', 'Unknown'),
                'confidence': round(similarity, 1),
                'molecular_weight': metadata.get('molecular_weight', 'N/A'),
                'bbb_permeable': metadata.get('bbb_permeable', False),
                'passes_lipinski': metadata.get('passes_lipinski', False),
                'clinical_trials': metadata.get('clinical_trials_count', 0),
                'pubchem_cid': metadata.get('pubchem_cid')
            })
        
        return candidates