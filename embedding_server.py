#!/usr/bin/env python3
"""
Simple embedding server that uses sentence-transformers/all-MiniLM-L6-v2
to provide a consistent embedding interface.
"""

from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import numpy as np

app = Flask(__name__)

# Load the model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

@app.route('/embed', methods=['POST'])
def embed():
    data = request.json
    inputs = data.get('inputs', [])
    
    if isinstance(inputs, str):
        inputs = [inputs]
    
    # Generate embeddings
    embeddings = model.encode(inputs)
    
    # Convert to list for JSON serialization
    if len(embeddings.shape) == 1:
        embeddings = embeddings.reshape(1, -1)
    
    result = embeddings.tolist()
    
    return jsonify({
        'embeddings': result,
        'model': 'sentence-transformers/all-MiniLM-L6-v2',
        'dimensions': len(result[0]) if result else 0
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model': 'sentence-transformers/all-MiniLM-L6-v2'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
