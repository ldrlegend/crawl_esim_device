from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import subprocess
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="eSIM Crawler Webhook", version="1.0.0")

class WebhookData(BaseModel):
    trigger: Optional[str] = "manual"
    metadata: Optional[Dict[str, Any]] = None

@app.post("/webhook")
async def webhook_trigger(data: WebhookData = WebhookData()):
    """Webhook endpoint that triggers the eSIM crawler"""
    try:
        logger.info(f"Webhook triggered with data: {data.model_dump()}")
        
        # Run the main crawler
        result = subprocess.run(
            ["python", "main.py"], 
            capture_output=True, 
            text=True,
            cwd=os.getcwd()  # Run from current directory
        )
        
        if result.returncode == 0:
            logger.info("Crawler completed successfully")
            return {
                "status": "success",
                "message": "eSIM crawler completed successfully",
                "data": data.model_dump(),
                "crawler_output": result.stdout,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"Crawler failed: {result.stderr}")
            return {
                "status": "error",
                "message": "eSIM crawler failed",
                "error": result.stderr,
                "data": data.model_dump(),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "service": "eSIM Crawler Webhook",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with usage information"""
    return {
        "service": "eSIM Crawler Webhook",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "POST /webhook - Trigger eSIM device crawling",
            "health": "GET /health - Health check",
            "root": "GET / - This information"
        },
        "usage": "Send POST request to /webhook with any JSON data to trigger crawling"
    }