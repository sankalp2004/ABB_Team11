from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import upload, training, simulation

app = FastAPI(title="MiniML - Predictive Quality Control Backend API")

# Configure CORS for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(training.router, tags=["Training"])
app.include_router(simulation.router, tags=["Simulation"])

@app.get("/")
def read_root():
    return {"message": "Welcome to MiniML - Predictive Quality Control Backend API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "miniml-backend"}