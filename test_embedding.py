#!/usr/bin/env python3

import os
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from sentence_transformers import SentenceTransformer

# Test the embedding model directly
print("Testing embedding models...")

# Test 1: sentence-transformers directly
print("\n1. Testing sentence-transformers directly:")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embedding = model.encode("test text")
print(f"Direct sentence-transformers dimension: {len(embedding)}")

# Test 2: HuggingFaceBgeEmbeddings
print("\n2. Testing HuggingFaceBgeEmbeddings:")
try:
    embeddings = HuggingFaceBgeEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    embedding = embeddings.embed_query("test text")
    print(f"HuggingFaceBgeEmbeddings dimension: {len(embedding)}")
except Exception as e:
    print(f"Error with HuggingFaceBgeEmbeddings: {e}")

# Test 3: Check if the model is being downloaded correctly
print("\n3. Testing model loading:")
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    embedding = embeddings.embed_query("test text")
    print(f"HuggingFaceEmbeddings dimension: {len(embedding)}")
except Exception as e:
    print(f"Error with HuggingFaceEmbeddings: {e}")
