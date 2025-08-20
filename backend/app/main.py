from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, training, simulation

app = FastAPI(title="IntelliInspect Backend API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Allows Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(training.router, prefix="/api", tags=["Training"])
app.include_router(simulation.router, prefix="/api", tags=["Simulation"])

# Mount the websocket endpoint at the root level
app.include_router(simulation.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the IntelliInspect Backend"}