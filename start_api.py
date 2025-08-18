#!/usr/bin/env python3
"""
Start FastAPI server for eSIM crawler webhook
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting FastAPI eSIM Crawler Webhook Server")
    print("📋 Health check: http://localhost:8000/health")
    print("🌐 Webhook endpoint: http://localhost:8000/webhook")
    print("📖 API docs: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )