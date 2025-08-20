import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
import httpx
from app.datastore import mem_store
from app.websocket_manager import manager

router = APIRouter()
ML_SERVICE_URL = "http://ml-service-python:8000"

async def run_simulation_logic():
    """The background task for running the simulation."""
    if 'dataset' not in mem_store or 'date_ranges' not in mem_store:
        await manager.broadcast_json({"status": "Error", "message": "Dataset or ranges not configured."})
        return

    df = mem_store['dataset']
    ranges = mem_store['date_ranges']
    sim_df = df[(df['synthetic_timestamp'] >= ranges.simStart) & (df['synthetic_timestamp'] <= ranges.simEnd)]

    if sim_df.empty:
        await manager.broadcast_json({"status": "Complete", "message": "No data in simulation period."})
        return

    async with httpx.AsyncClient() as client:
        for _, row in sim_df.iterrows():
            row_data = row.to_dict()
            # Convert timestamp to string for JSON serialization
            row_data['synthetic_timestamp'] = row_data['synthetic_timestamp'].isoformat()

            try:
                response = await client.post(f"{ML_SERVICE_URL}/predict", json={"data": row_data})
                if response.status_code == 200:
                    prediction_result = response.json()
                    await manager.broadcast_json({
                        "type": "prediction",
                        "payload": {
                            "timestamp": row_data['synthetic_timestamp'],
                            "sampleId": row_data.get('Id', 'N/A'),
                            "prediction": prediction_result
                        }
                    })
                else:
                     await manager.broadcast_json({"type": "error", "message": f"Prediction failed for row"})

            except httpx.RequestError:
                 await manager.broadcast_json({"type": "error", "message": "ML service is unavailable"})

            await asyncio.sleep(1) # Simulate real-time 1-second interval

    await manager.broadcast_json({"type": "status", "message": "Simulation completed!"})


@router.post("/simulation/start")
async def start_simulation(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_simulation_logic)
    return {"message": "Simulation started."}


@router.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)