import json
import os
from typing import Dict, Any
from utils.logger import setup_logger

class Config:
    def __init__(self, config_path: str = "config.json"):
        self.logger = setup_logger()
        self.config_path = config_path
        self.default_config = {
            "theme": "dark",
            "performance_mode": "performance",
            "cache_enabled": True,
            "max_tokens": 2048,
            "temperature": 0.7,
            "voice_enabled": True
        }
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {**self.default_config, **config}
            else:
                self.save_config(self.default_config)
                return self.default_config
                
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return self.default_config
            
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")
            
    def get_theme(self) -> str:
        """Get current theme setting"""
        return self.config.get("theme", "dark")
        
    def set_theme(self, theme: str):
        """Set theme and save configuration"""
        self.config["theme"] = theme
        self.save_config(self.config)
        
    def get_performance_mode(self) -> str:
        """Get current performance mode"""
        return self.config.get("performance_mode", "performance")
        
    def set_performance_mode(self, mode: str):
        """Set performance mode and save configuration"""
        self.config["performance_mode"] = mode
        self.save_config(self.config)
        
    def get_temperature(self) -> float:
        """Get current temperature setting"""
        return self.config.get("temperature", 0.7)
        
    def set_temperature(self, temp: float):
        """Set temperature and save configuration"""
        self.config["temperature"] = temp
        self.save_config(self.config)
        
    def is_cache_enabled(self) -> bool:
        """Check if semantic cache is enabled"""
        return self.config.get("cache_enabled", True)
        
    def set_cache_enabled(self, enabled: bool):
        """Enable/disable semantic cache"""
        self.config["cache_enabled"] = enabled
        self.save_config(self.config)
        
    def is_voice_enabled(self) -> bool:
        """Check if voice input is enabled"""
        return self.config.get("voice_enabled", True)
        
    def set_voice_enabled(self, enabled: bool):
        """Enable/disable voice input"""
        self.config["voice_enabled"] = enabled
        self.save_config(self.config) 