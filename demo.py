import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

# Set random seed for reproducibility
np.random.seed(42)

# Create fake drug clusters (simulating high-dimensional embeddings reduced to 2D)
n_drugs_per_cluster = 15

# Cluster 1: Anti-inflammatory drugs
anti_inflammatory = np.random.randn(n_drugs_per_cluster, 2) * 0.3 + np.array([2, 2])

# Cluster 2: Cardiovascular drugs
cardiovascular = np.random.randn(n_drugs_per_cluster, 2) * 0.3 + np.array([5, 4])

# Cluster 3: Antibiotics
antibiotics = np.random.randn(n_drugs_per_cluster, 2) * 0.3 + np.array([1, 5])

# Cluster 4: Neurological drugs
neurological = np.random.randn(n_drugs_per_cluster, 2) * 0.3 + np.array([4, 1])

# Highlight drugs
aspirin = np.array([[2.2, 2.3]])  # In anti-inflammatory cluster
query_drug = np.array([[2.0, 1.8]])  # New drug we're querying

# Create plot
plt.figure(figsize=(10, 7))

# Plot clusters
plt.scatter(anti_inflammatory[:, 0], anti_inflammatory[:, 1], 
           c='#FF6B6B', s=100, alpha=0.6, label='Anti-inflammatory', edgecolors='black', linewidth=1)
plt.scatter(cardiovascular[:, 0], cardiovascular[:, 1], 
           c='#4ECDC4', s=100, alpha=0.6, label='Cardiovascular', edgecolors='black', linewidth=1)
plt.scatter(antibiotics[:, 0], antibiotics[:, 1], 
           c='#95E1D3', s=100, alpha=0.6, label='Antibiotics', edgecolors='black', linewidth=1)
plt.scatter(neurological[:, 0], neurological[:, 1], 
           c='#F38181', s=100, alpha=0.6, label='Neurological', edgecolors='black', linewidth=1)

# Highlight special drugs
plt.scatter(aspirin[:, 0], aspirin[:, 1], 
           c='gold', s=300, marker='*', edgecolors='black', linewidth=2, label='Aspirin', zorder=5)
plt.scatter(query_drug[:, 0], query_drug[:, 1], 
           c='lime', s=300, marker='D', edgecolors='black', linewidth=2, label='Query Drug', zorder=5)

# Draw arrow from query to nearest cluster
plt.arrow(query_drug[0, 0], query_drug[0, 1], 
         aspirin[0, 0] - query_drug[0, 0] - 0.1, 
         aspirin[0, 1] - query_drug[0, 1] - 0.1,
         head_width=0.15, head_length=0.1, fc='red', ec='red', linewidth=2, zorder=4)

plt.text(1.5, 1.2, 'FAISS finds\nsimilar drugs', fontsize=12, color='red', weight='bold')

# Labels and styling
plt.xlabel('Embedding Dimension 1', fontsize=12, weight='bold')
plt.ylabel('Embedding Dimension 2', fontsize=12, weight='bold')
plt.title('Vector Space: Drugs Clustered by Mechanism Similarity\n(2D projection of 384D embeddings)', 
         fontsize=14, weight='bold', pad=20)
plt.legend(loc='upper left', fontsize=10, framealpha=0.9)
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()

# Save
plt.savefig('drug_embedding_space.png', dpi=300, bbox_inches='tight', facecolor='white')
print("Saved as 'drug_embedding_space.png'")
plt.show()
