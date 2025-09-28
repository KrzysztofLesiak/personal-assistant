"""
Logging configuration module that provides colored logging
"""

import logging
import sys

def setup_colored_logging(level: int = logging.INFO) -> None:
    """
    Setup colored logging
    
    Args:
        level: Logging level (default: INFO)
    """
    class ColoredFormatter(logging.Formatter):
        """Custom formatter with colors matching uvicorn's style - only colors the log level"""
        
        # ANSI color codes
        COLORS = {
            'DEBUG': '\033[36m',      # Cyan
            'INFO': '\033[32m',       # Green  
            'WARNING': '\033[33m',    # Yellow
            'ERROR': '\033[31m',      # Red
            'CRITICAL': '\033[35m',   # Magenta
        }
        RESET = '\033[0m'
        
        def format(self, record):
            # Get the color for this log level
            color = self.COLORS.get(record.levelname, '')
            
            # Apply color only to the levelname if outputting to a terminal
            if sys.stderr.isatty():
                colored_levelname = f"{color}{record.levelname}{self.RESET}"
            else:
                colored_levelname = record.levelname
            
            # Format timestamp in ISO format (similar to uvicorn's default)
            timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
            
            # Format the message with timestamp, colored level name, and message
            return f"{timestamp} | {colored_levelname}:     {record.getMessage()}"
    
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter())
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=[handler],
        force=True  # Override any existing configuration
    )
    
    # Configure uvicorn loggers to use our formatter
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers.clear()
    uvicorn_logger.addHandler(handler)
    uvicorn_logger.setLevel(level)
    uvicorn_logger.propagate = False
    
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.handlers.clear()
    uvicorn_error_logger.addHandler(handler)
    uvicorn_error_logger.setLevel(level)
    uvicorn_error_logger.propagate = False
    
    # Configure FastAPI logger
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.handlers.clear()
    fastapi_logger.addHandler(handler)
    fastapi_logger.setLevel(level)
    fastapi_logger.propagate = False
    
    # Disable uvicorn's access logging to avoid duplicates (we use --no-access-log flag)
    logging.getLogger("uvicorn.access").disabled = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)