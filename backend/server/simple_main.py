from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/test")
async def api_test():
    return {"test": "success", "message": "API v1 test endpoint"}

@app.get("/api/v1/auth/test")
async def auth_test():
    return {"auth": "authentication test endpoint"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
