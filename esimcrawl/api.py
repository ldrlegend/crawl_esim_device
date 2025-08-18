from fastapi import FastAPI, Request
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="eSIM Crawler Webhook", version="1.0.0")

@app.post("/webhook")
async def webhook_trigger(request: Request):
    """Webhook endpoint that triggers the eSIM crawler"""
    try:
        # Get the POST data
        data = await request.json()
        logger.info(f"Webhook triggered with data: {data}")
        
        # Run the main crawler
        result = subprocess.run(
            ["python", "main.py"], 
            capture_output=True, 
            text=True,
            cwd="."  # Run from current directory
        )
        
        if result.returncode == 0:
            logger.info("Crawler completed successfully")
            return {
                "status": "success",
                "message": "eSIM crawler completed successfully",
                "data": data,
                "crawler_output": result.stdout
            }
        else:
            logger.error(f"Crawler failed: {result.stderr}")
            return {
                "status": "error",
                "message": "eSIM crawler failed",
                "error": result.stderr,
                "data": data
            }
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "eSIM Crawler Webhook"}

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
