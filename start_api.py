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
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )