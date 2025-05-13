import customtkinter as ctk
from typing import Optional, Callable
import threading
import asyncio
import markdown
from tkinter import scrolledtext
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import filedialog, messagebox

print("Iniciando ChatApplication")

class ChatWindow:
    def __init__(self, master: ctk.CTk, app):
        self.master = master
        self.app = app
        self.setup_ui()
        self.is_recording = False
        self.audio_data = []
        self.last_assistant_index = None
        
        print("Iniciando ChatWindow")
        
    def setup_ui(self):
        """Initialize UI components"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.master)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame,
            wrap="word",
            font=("Segoe UI", 11),
            bg="#2b2b2b",
            fg="#ffffff",
            height=20
        )
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Input frame
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(fill="x", padx=5, pady=5)
        
        # Message input
        self.message_input = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type your message...",
            font=("Segoe UI", 11)
        )
        self.message_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.message_input.bind("<Return>", self.send_message)
        
        # Voice recording button
        self.voice_button = ctk.CTkButton(
            self.input_frame,
            text="🎤",
            width=40,
            command=self.toggle_recording
        )
        self.voice_button.pack(side="right", padx=(5, 0))
        
        # Temperature slider
        self.temp_frame = ctk.CTkFrame(self.main_frame)
        self.temp_frame.pack(fill="x", padx=5, pady=5)
        
        self.temp_label = ctk.CTkLabel(
            self.temp_frame,
            text="Temperature:"
        )
        self.temp_label.pack(side="left", padx=5)
        
        self.temp_slider = ctk.CTkSlider(
            self.temp_frame,
            from_=0.1,
            to=1.0,
            number_of_steps=9,
            command=self.update_temperature
        )
        self.temp_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.temp_slider.set(0.7)
        
        self.temp_value = ctk.CTkLabel(
            self.temp_frame,
            text="0.7"
        )
        self.temp_value.pack(side="right", padx=5)
        
        self.pdf_button = ctk.CTkButton(
            self.main_frame,
            text="Exportar PDF",
            command=self.export_chat_to_pdf
        )
        self.pdf_button.pack(pady=10)
        
    def update_temperature(self, value):
        """Update temperature value display and model setting"""
        self.temp_value.configure(text=f"{value:.1f}")
        self.app.ollama_client.set_temperature(float(value))
        
    def send_message(self, event=None):
        """Send message to chat"""
        message = self.message_input.get().strip()
        if not message:
            return
            
        self.message_input.delete(0, "end")
        self.add_message("You", message)
        
        # Start response generation in separate thread
        threading.Thread(target=self.generate_response, args=(message,)).start()
        
    def generate_response(self, message: str):
        """Generate response from model"""
        def run_async():
            async def _generate():
                response_text = ""
                first_chunk = True
                async for chunk in self.app.ollama_client.generate(message):
                    response_text += chunk
                    # Só adiciona a mensagem do assistente uma vez
                    if first_chunk:
                        self.add_message("Assistant", "")
                        first_chunk = False
                    self.update_response("Assistant", response_text)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_generate())
            loop.close()
        run_async()
        
    def add_message(self, sender: str, message: str):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert("end", f"\n[{timestamp}] {sender}:\n")
        self.chat_display.insert("end", f"{message}\n")
        self.chat_display.see("end")
        # Salva o índice do início da última resposta do assistente
        if sender == "Assistant":
            self.last_assistant_index = self.chat_display.index("end-2l")
        
    def update_response(self, sender: str, message: str):
        """Update streaming response in chat"""
        # Atualiza apenas a última resposta do assistente
        if hasattr(self, "last_assistant_index") and self.last_assistant_index:
            # Remove apenas o texto da última resposta do assistente
            self.chat_display.delete(self.last_assistant_index, "end-1c")
            self.chat_display.insert(self.last_assistant_index, f"{message}\n")
            self.chat_display.see("end")
        
    def toggle_recording(self):
        """Toggle voice recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start voice recording"""
        self.is_recording = True
        self.voice_button.configure(text="⏹", fg_color="red")
        self.audio_data = []
        
        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_data.extend(indata.copy())
            
        self.stream = sd.InputStream(callback=callback)
        self.stream.start()
        
    def stop_recording(self):
        """Stop voice recording and process audio"""
        self.is_recording = False
        self.voice_button.configure(text="🎤", fg_color=["#3B8ED0", "#1F6AA5"])
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            
        if self.audio_data:
            # Convert audio data to text using Whisper
            audio_array = np.array(self.audio_data)
            text = self.app.voice_handler.transcribe(audio_array)
            
            if text:
                self.message_input.delete(0, "end")
                self.message_input.insert(0, text)
                self.send_message() 

    def export_chat_to_pdf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Salvar relatório do chat como PDF"
        )
        if not file_path:
            return

        chat_text = self.chat_display.get("1.0", "end-1c")

        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            margin = 40
            y = height - margin
            for line in chat_text.split('\n'):
                c.drawString(margin, y, line)
                y -= 14
                if y < margin:
                    c.showPage()
                    y = height - margin
            c.save()
            messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}") 