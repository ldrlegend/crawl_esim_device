"""
Configuration settings for the eSIM device crawler.
"""

import os
from typing import Dict, Any

# Webhook Configuration
WEBHOOK_CONFIG = {
    "url": os.getenv("WEBHOOK_URL", "https://n8n.gohub.cloud/webhook/eSIM_compatible"),
    "timeout": int(os.getenv("WEBHOOK_TIMEOUT", "30")),
    "retries": int(os.getenv("WEBHOOK_RETRIES", "3")),
    "headers": {
        "Content-Type": "application/json",
        "User-Agent": "eSIM-Crawler/1.0"
    }
}

# File Paths
FILE_PATHS = {
    "json_output": "yesim_devices.json",
    "log_file": "esim_crawler.log",
    "rendered_page": "rendered_page.html"
}

# Scrapy Configuration
SCRAPY_CONFIG = {
    "timeout": int(os.getenv("SCRAPY_TIMEOUT", "300")),  # 5 minutes
    "spider_name": "yesim_devices"
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file_handler": True,
    "console_handler": True
}

# Development/Production mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# All configuration combined
CONFIG: Dict[str, Any] = {
    "webhook": WEBHOOK_CONFIG,
    "files": FILE_PATHS,
    "scrapy": SCRAPY_CONFIG,
    "logging": LOGGING_CONFIG,
    "debug": DEBUG
}
