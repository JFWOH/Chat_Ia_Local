import logging
import os
from datetime import datetime

def setup_logger(name: str = "chat_app") -> logging.Logger:
    """Setup and configure application logger"""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(
        f"logs/chat_errors_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    # Set levels
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.ERROR)
    
    # Create formatters
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
        'File: %(pathname)s\n'
        'Line: %(lineno)d\n'
        'Function: %(funcName)s\n'
        'Stack Trace:\n%(exc_info)s\n'
    )
    
    # Set formatters
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger 