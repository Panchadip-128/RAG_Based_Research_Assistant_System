# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import fitz  # PyMuPDF for lightweight PDF processing
from pathlib import Path
import re
from typing import List, Dict, Any
from comps import CustomLogger

logger = CustomLogger("light_processor")

class LightDocumentProcessor:
    """
    Lightweight document processor that uses simple text extraction
    instead of heavy AI models for layout recognition and OCR.
    """
    
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process PDF using lightweight PyMuPDF instead of heavy AI models.
        """
        try:
            doc = fitz.open(file_path)
            chunks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text without OCR
                text = page.get_text()
                
                if text.strip():
                    # Simple text cleaning
                    text = self._clean_text(text)
                    
                    # Split into chunks
                    page_chunks = self._split_text(text, page_num + 1)
                    chunks.extend(page_chunks)
                    
                    logger.info(f"Processed page {page_num + 1}, extracted {len(page_chunks)} chunks")
            
            doc.close()
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """Simple text cleaning without heavy processing."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers (simple pattern)
        text = re.sub(r'\b\d+\b\s*$', '', text)
        return text.strip()
    
    def _split_text(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Split text into chunks without heavy processing."""
        chunks = []
        
        # Simple chunking by sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'page': page_num,
                    'source': f"page_{page_num}"
                })
                current_chunk = sentence
            else:
                current_chunk += (" " + sentence if current_chunk else sentence)
        
        # Add final chunk if it exists
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'page': page_num,
                'source': f"page_{page_num}"
            })
        
        return chunks
    
    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Main entry point for document processing."""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.pdf':
            return self.process_pdf(str(file_path))
        else:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return []
