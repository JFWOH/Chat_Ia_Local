import customtkinter as ctk
import asyncio
import threading
from typing import Optional, Dict, List
import json
import logging
from datetime import datetime
import os
import aiohttp
from typing import AsyncGenerator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import filedialog, messagebox

from backend.ollama_client import OllamaClient
from backend.semantic_cache import SemanticCache
from backend.voice_handler import VoiceHandler
from gui.chat_window import ChatWindow
from utils.config import Config
from utils.logger import setup_logger

class ChatApplication:
    def __init__(self):
        self.setup_logging()
        self.config = Config()
        self.setup_theme()
        
        # Initialize components
        self.ollama_client = OllamaClient(model_name="phi3-mini")
        self.semantic_cache = SemanticCache()
        self.voice_handler = VoiceHandler()
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Local Chat IA")
        self.root.geometry("1200x800")
        
        # Initialize GUI
        self.chat_window = ChatWindow(self.root, self)
        
        # Performance monitoring
        self.setup_performance_monitoring()
        
    def setup_logging(self):
        """Configure logging for the application"""
        self.logger = setup_logger()
        
    def setup_theme(self):
        """Configure application theme"""
        ctk.set_appearance_mode(self.config.get_theme())
        ctk.set_default_color_theme("blue")
        
    def setup_performance_monitoring(self):
        """Initialize performance monitoring"""
        self.performance_mode = self.config.get_performance_mode()
        self.rate_limiter = RateLimiter(max_requests=5, time_window=60)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()
        
    async def process_message(self, message: str) -> str:
        """Process incoming messages with caching and fallback"""
        try:
            # Check rate limit
            if not self.rate_limiter.check():
                return "Rate limit exceeded. Please wait."
                
            # Check cache
            cached_response = self.semantic_cache.get(message)
            if cached_response:
                return cached_response
                
            # Generate response
            response = await self.ollama_client.generate(message)
            
            # Cache response
            self.semantic_cache.add(message, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return "An error occurred. Please try again."

    def generate_response(self, message: str):
        self.chat_window.generate_response(message)

    def export_chat_to_pdf(self):
        # Abre diálogo para escolher onde salvar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Salvar relatório do chat como PDF"
        )
        if not file_path:
            return

        # Pega o texto do chat
        chat_text = self.chat_window.chat_display.get("1.0", "end-1c")

        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            margin = 40
            y = height - margin
            for line in chat_text.split('\n'):
                c.drawString(margin, y, line)
                y -= 14  # Espaçamento entre linhas
                if y < margin:
                    c.showPage()
                    y = height - margin
            c.save()
            messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        
    def check(self) -> bool:
        """Check if request is within rate limits"""
        now = datetime.now()
        self.requests = [req for req in self.requests 
                        if (now - req).total_seconds() < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            return False
            
        self.requests.append(now)
        return True

if __name__ == "__main__":
    app = ChatApplication()
    app.run() 