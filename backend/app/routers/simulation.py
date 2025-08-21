from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime
import random

router = APIRouter()

# Store simulation state in memory (in production, use a database)
simulation_state = {
    "is_running": False,
    "predictions": [],
    "stats": {
        "total_predictions": 0,
        "out_of_range": 0,
        "accuracy": 0
    }
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

class SimulationStartRequest(BaseModel):
    pass

class SimulationStopRequest(BaseModel):
    pass

@router.post("/simulation/start")
async def start_simulation(request: SimulationStartRequest):
    """
    Start the simulation process
    """
    try:
        simulation_state.update({
            "is_running": True,
            "started_at": datetime.now().isoformat(),
            "predictions": [],
            "stats": {
                "total_predictions": 0,
                "out_of_range": 0,
                "accuracy": 0
            }
        })
        
        return {
            "success": True,
            "message": "Simulation started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting simulation: {str(e)}")

@router.post("/simulation/stop")
async def stop_simulation(request: SimulationStopRequest):
    """
    Stop the simulation process
    """
    try:
        simulation_state.update({
            "is_running": False,
            "stopped_at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": "Simulation stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping simulation: {str(e)}")

@router.get("/simulation/status")
async def get_simulation_status():
    """
    Get current simulation status
    """
    return {
        "success": True,
        "data": simulation_state
    }

@router.get("/simulation/predictions")
async def get_predictions():
    """
    Get all predictions from the current simulation
    """
    return {
        "success": True,
        "data": {
            "predictions": simulation_state["predictions"],
            "stats": simulation_state["stats"]
        }
    }

@router.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time simulation data
    """
    await manager.connect(websocket)
    try:
        while True:
            # Send real-time data every 2 seconds
            await asyncio.sleep(2)
            
            if simulation_state["is_running"]:
                # Generate a new prediction
                prediction = generate_prediction()
                simulation_state["predictions"].append(prediction)
                simulation_state["stats"]["total_predictions"] += 1
                
                if prediction["prediction"] == "Fail":
                    simulation_state["stats"]["out_of_range"] += 1
                
                # Calculate accuracy
                correct_predictions = len([p for p in simulation_state["predictions"] if p["correct"]])
                simulation_state["stats"]["accuracy"] = (
                    correct_predictions / len(simulation_state["predictions"]) * 100
                    if simulation_state["predictions"] else 0
                )
                
                # Send to all connected clients
                await manager.broadcast(json.dumps({
                    "type": "prediction",
                    "data": prediction,
                    "stats": simulation_state["stats"]
                }))
            else:
                # Send status update
                await manager.broadcast(json.dumps({
                    "type": "status",
                    "data": simulation_state
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def generate_prediction():
    """
    Generate a simulated prediction
    """
    now = datetime.now()
    sample_id = f"SAMPLE-{random.randint(100, 999)}"
    prediction = "Pass" if random.random() > 0.2 else "Fail"
    confidence = random.randint(80, 100)
    computation_time = random.randint(50, 150)
    threshold = 85
    correct = random.random() > 0.1  # 90% accuracy
    
    return {
        "time": now.strftime("%I:%M %p"),
        "sample_id": sample_id,
        "prediction": prediction,
        "confidence": confidence,
        "computation_time": computation_time,
        "threshold": threshold,
        "correct": correct
    }