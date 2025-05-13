import aiohttp
import json
import asyncio
from typing import AsyncGenerator, Optional
import logging
import pynvml
from utils.logger import setup_logger

class OllamaClient:
    def __init__(self, model_name="phi3-mini"):
        self.logger = setup_logger()
        self.base_url = "http://localhost:11434/api"
        self.model = model_name
        self.temperature = 0.7
        self.max_tokens = 2048
        self.setup_gpu_monitoring()
        
    def setup_gpu_monitoring(self):
        """Initialize GPU monitoring"""
        try:
            pynvml.nvmlInit()
            self.has_gpu = True
        except:
            self.has_gpu = False
            self.logger.warning("No NVIDIA GPU detected, falling back to CPU mode")
            
    def check_gpu_memory(self) -> bool:
        """Check if GPU has enough memory"""
        if not self.has_gpu:
            return False
            
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            return info.free > 2 * 1024 * 1024 * 1024  # 2GB free
        except:
            return False
            
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate response from Ollama with streaming"""
        if self.has_gpu and not self.check_gpu_memory():
            self.logger.warning("GPU memory low, falling back to CPU mode")
            
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            try:
                async with session.post(f"{self.base_url}/generate", json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"Ollama API error: {response.status}")
                        
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                            except json.JSONDecodeError:
                                continue
                                
            except Exception as e:
                self.logger.error(f"Error in generate: {str(e)}")
                yield f"Error: {str(e)}"
                
    def set_temperature(self, temp: float):
        """Set model temperature"""
        self.temperature = max(0.1, min(1.0, temp))
        
    def set_model(self, model_name: str):
        """Set model name"""
        self.model = model_name 