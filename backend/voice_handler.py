import numpy as np
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
from utils.logger import setup_logger

class VoiceHandler:
    def __init__(self):
        self.logger = setup_logger()
        self.setup_whisper()
        
    def setup_whisper(self):
        """Initialize Whisper model"""
        try:
            self.processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
            self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
            
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
                self.logger.info("Whisper model loaded on GPU")
            else:
                self.logger.info("Whisper model loaded on CPU")
                
        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {str(e)}")
            self.model = None
            self.processor = None
            
    def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio data to text"""
        if self.model is None or self.processor is None:
            self.logger.error("Whisper model not initialized")
            return ""
            
        try:
            # Prepare audio data
            audio_data = audio_data.astype(np.float32)
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
                
            # Normalize audio
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Process audio
            input_features = self.processor(
                audio_data,
                sampling_rate=16000,
                return_tensors="pt"
            ).input_features
            
            if torch.cuda.is_available():
                input_features = input_features.to("cuda")
                
            # Generate transcription
            predicted_ids = self.model.generate(input_features)
            transcription = self.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True
            )[0]
            
            return transcription.strip()
            
        except Exception as e:
            self.logger.error(f"Error in transcription: {str(e)}")
            return "" 