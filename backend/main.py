import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AutoScrum API")

# Get frontend URL from environment or use default
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://autoscrum-ai-autonomous-agile-orchestration-pipe-production.up.railway.app")

# Configure CORS - CRITICAL for web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8501"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AutoScrum API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "frontend_url": FRONTEND_URL}

# Add your other API routes here

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
