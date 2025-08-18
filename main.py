import json
import logging
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

import requests
from requests.exceptions import RequestException

# Try to import config, fallback to default if not available
try:
    from config import CONFIG
except ImportError:
    # Fallback configuration if config.py is not available
    CONFIG = {
        "webhook": {
            "url": "https://n8n.gohub.cloud/webhook/eSIM_compatible",
            "timeout": 30,
            "retries": 3,
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "eSIM-Crawler/1.0"
            }
        },
        "files": {
            "json_output": "yesim_devices.json",
            "log_file": "esim_crawler.log",
            "rendered_page": "rendered_page.html"
        },
        "scrapy": {
            "timeout": 300,
            "spider_name": "yesim_devices"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "file_handler": True,
            "console_handler": True
        },
        "debug": False
    }

# Configure logging
log_level = getattr(logging, CONFIG["logging"]["level"].upper())
handlers = []

if CONFIG["logging"]["file_handler"]:
    handlers.append(logging.FileHandler(CONFIG["files"]["log_file"]))

if CONFIG["logging"]["console_handler"]:
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=log_level,
    format=CONFIG["logging"]["format"],
    handlers=handlers
)
logger = logging.getLogger(__name__)


def run_scrapy_crawl() -> bool:
    """
    Run the Scrapy spider to crawl device data.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Starting Scrapy crawl...")
        result = subprocess.run(
            ["scrapy", "crawl", CONFIG["scrapy"]["spider_name"]],
            capture_output=True,
            text=True,
            timeout=CONFIG["scrapy"]["timeout"]
        )
        
        if result.returncode == 0:
            logger.info("Scrapy crawl completed successfully")
            return True
        else:
            logger.error(f"Scrapy crawl failed with return code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Scrapy crawl timed out after {CONFIG['scrapy']['timeout']} seconds")
        return False
    except FileNotFoundError:
        logger.error("Scrapy command not found. Make sure Scrapy is installed and in PATH")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during Scrapy crawl: {e}")
        return False


def load_json_data(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load JSON data from file with error handling.
    Handles both single JSON objects and JSONLines format (multiple JSON objects, one per line).
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dict containing the JSON data or None if failed
    """
    try:
        json_path = Path(file_path)
        if not json_path.exists():
            logger.error(f"JSON file not found: {file_path}")
            return None
            
        with open(json_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        # Try to parse as single JSON object first
        try:
            data = json.loads(content)
            logger.info(f"Successfully loaded single JSON object from {file_path}")
            return data
        except json.JSONDecodeError:
            # If that fails, try to parse as JSONLines (multiple JSON objects)
            logger.info(f"Attempting to parse {file_path} as JSONLines format")
            
            # Split by lines and parse each valid JSON object
            lines = content.split('\n')
            json_objects = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    obj = json.loads(line)
                    json_objects.append(obj)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON on line {line_num}: {e}")
                    continue
            
            if json_objects:
                logger.info(f"Successfully loaded {len(json_objects)} JSON objects from {file_path}")
                return {"items": json_objects}
            else:
                logger.error(f"No valid JSON objects found in {file_path}")
                return None
                
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return None


def send_webhook_data(data: Dict[str, Any], url: str, timeout: int = 30, retries: int = 3) -> bool:
    """
    Send data to webhook with retry logic and error handling.
    
    Args:
        data: Data to send
        url: Webhook URL
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        
    Returns:
        bool: True if successful, False otherwise
    """
    for attempt in range(retries):
        try:
            logger.info(f"Sending data to webhook (attempt {attempt + 1}/{retries})")
            
            response = requests.post(
                url,
                json=data,
                timeout=timeout,
                headers=CONFIG["webhook"]["headers"]
            )
            
            logger.info(f"Webhook response status: {response.status_code}")
            logger.info(f"Webhook response: {response.text}")
            
            if response.status_code == 200:
                logger.info("Data sent successfully to webhook")
                return True
            else:
                logger.warning(f"Webhook returned non-200 status: {response.status_code}")
                
        except RequestException as e:
            logger.error(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt == retries - 1:
                logger.error("All retry attempts failed")
                return False
        except Exception as e:
            logger.error(f"Unexpected error sending webhook data: {e}")
            return False
    
    return False


def cleanup_files() -> None:
    """
    Clean up temporary files created by the script.
    """
    logger.info("Starting file cleanup...")
    files_to_delete = [
        CONFIG["files"]["json_output"],
        CONFIG["files"]["rendered_page"]
    ]
    
    for file_path in files_to_delete:
        if Path(file_path).exists():
            try:
                Path(file_path).unlink()
                logger.info(f"Deleted {file_path}")
            except OSError as e:
                logger.error(f"Error deleting {file_path}: {e}")
        else:
            logger.info(f"{file_path} not found, skipping deletion.")
    
    # Try to clean log file but don't fail if it's in use
    log_file = CONFIG["files"]["log_file"]
    if Path(log_file).exists():
        try:
            Path(log_file).unlink()
            logger.info(f"Deleted {log_file}")
        except OSError as e:
            logger.info(f"Could not delete {log_file} (file may be in use): {e}")
    
    logger.info("File cleanup completed.")


def main() -> None:
    """
    Main function to orchestrate the crawling and webhook sending process.
    """
    logger.info("Starting eSIM device crawling process")
    
    if CONFIG["debug"]:
        logger.info("Running in DEBUG mode")
    
    # Step 0: Clean up previous files
    cleanup_files()
    
    # Step 1: Run Scrapy crawl
    if not run_scrapy_crawl():
        logger.error("Failed to run Scrapy crawl. Exiting.")
        sys.exit(1)
    
    # Step 2: Load JSON data
    json_data = load_json_data(CONFIG["files"]["json_output"])
    if json_data is None:
        logger.error("Failed to load JSON data. Exiting.")
        sys.exit(1)
    
    # Step 3: Send data to webhook
    if send_webhook_data(
        json_data, 
        CONFIG["webhook"]["url"], 
        CONFIG["webhook"]["timeout"], 
        CONFIG["webhook"]["retries"]
    ):
        logger.info("Process completed successfully")
    else:
        logger.error("Failed to send data to webhook")
        sys.exit(1)


if __name__ == "__main__":
    main()