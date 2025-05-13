import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Optional, Tuple
import json
from utils.logger import setup_logger
import os

class SemanticCache:
    def __init__(self, db_path: str = "cache/chat_cache.db", similarity_threshold: float = 0.85):
        # Garante que a pasta existe antes de criar o banco
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.logger = setup_logger()
        self.similarity_threshold = similarity_threshold
        self.db_path = db_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.setup_database()
        
    def setup_database(self):
        """Initialize SQLite database and create tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error setting up database: {str(e)}")
            
    def get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        return self.model.encode(text)
        
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
    def get(self, prompt: str) -> Optional[str]:
        """Get cached response if similar prompt exists"""
        try:
            prompt_embedding = self.get_embedding(prompt)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT prompt, response, embedding FROM cache")
            results = cursor.fetchall()
            
            for cached_prompt, response, cached_embedding in results:
                cached_embedding = np.frombuffer(cached_embedding, dtype=np.float32)
                similarity = self.cosine_similarity(prompt_embedding, cached_embedding)
                
                if similarity >= self.similarity_threshold:
                    self.logger.info(f"Cache hit with similarity {similarity:.2f}")
                    return response
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving from cache: {str(e)}")
            return None
            
        finally:
            conn.close()
            
    def add(self, prompt: str, response: str):
        """Add new prompt-response pair to cache"""
        try:
            embedding = self.get_embedding(prompt)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO cache (prompt, response, embedding) VALUES (?, ?, ?)",
                (prompt, response, embedding.tobytes())
            )
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Error adding to cache: {str(e)}")
            
        finally:
            conn.close()
            
    def clear(self):
        """Clear all cached entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cache")
            conn.commit()
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")
        finally:
            conn.close() 