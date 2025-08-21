from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import json
from datetime import datetime

router = APIRouter()

# Store training state and date ranges in memory (in production, use a database)
training_state = {
    "is_training": False,
    "progress": 0,
    "metrics": None,
    "training_data": []
}

date_ranges = {}

class DateRangeRequest(BaseModel):
    training: Dict[str, Any]
    testing: Dict[str, Any]
    simulation: Dict[str, Any]

class TrainingCompleteRequest(BaseModel):
    metrics: Dict[str, float]
    training_data: List[Dict[str, Any]]

@router.post("/date-ranges")
async def save_date_ranges(request: DateRangeRequest):
    """
    Save date ranges for training, testing, and simulation periods
    """
    try:
        date_ranges.update({
            "training": request.training,
            "testing": request.testing,
            "simulation": request.simulation,
            "saved_at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": "Date ranges saved successfully",
            "data": date_ranges
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving date ranges: {str(e)}")

@router.get("/date-ranges")
async def get_date_ranges():
    """
    Get saved date ranges
    """
    return {
        "success": True,
        "data": date_ranges
    }

@router.post("/training-complete")
async def training_complete(request: TrainingCompleteRequest):
    """
    Handle training completion with metrics
    """
    try:
        training_state.update({
            "is_training": False,
            "progress": 100,
            "metrics": request.metrics,
            "training_data": request.training_data,
            "completed_at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": "Training completed successfully",
            "data": {
                "metrics": request.metrics,
                "training_data": request.training_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing training completion: {str(e)}")

@router.get("/training-status")
async def get_training_status():
    """
    Get current training status
    """
    return {
        "success": True,
        "data": training_state
    }

@router.post("/start-training")
async def start_training():
    """
    Start the training process
    """
    try:
        training_state.update({
            "is_training": True,
            "progress": 0,
            "started_at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": "Training started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting training: {str(e)}")

@router.post("/stop-training")
async def stop_training():
    """
    Stop the training process
    """
    try:
        training_state.update({
            "is_training": False,
            "stopped_at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": "Training stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping training: {str(e)}")