from fastapi import APIRouter, HTTPException, Depends
import httpx
from app.datastore import mem_store
from app.models import DateRangePayload

router = APIRouter()
ML_SERVICE_URL = "http://ml-service-python:8000"

@router.post("/training/date-ranges")
async def set_date_ranges(payload: DateRangePayload):
    if 'dataset' not in mem_store:
        raise HTTPException(status_code=404, detail="Dataset not found. Please upload a file first.")

    df = mem_store['dataset']
    mem_store['date_ranges'] = payload

    def count_records(start, end):
        return df[(df['synthetic_timestamp'] >= start) & (df['synthetic_timestamp'] <= end)].shape[0]

    return {
        "status": "Valid",
        "trainingRecords": count_records(payload.trainStart, payload.trainEnd),
        "testingRecords": count_records(payload.testStart, payload.testEnd),
        "simulationRecords": count_records(payload.simStart, payload.simEnd)
    }

# FILE: backend/app/routers/training.py
# Replace the entire train_model function with this one.

# FILE: backend/app/routers/training.py
# Replace the entire train_model function with this one.

@router.post("/training/train-model")
async def train_model():
    if 'dataset' not in mem_store:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if 'date_ranges' not in mem_store:
        raise HTTPException(status_code=400, detail="Date ranges not set.")

    df = mem_store['dataset']
    ranges = mem_store['date_ranges']

    train_df = df[(df['synthetic_timestamp'] >= ranges.trainStart) & (df['synthetic_timestamp'] <= ranges.trainEnd)]
    test_df = df[(df['synthetic_timestamp'] >= ranges.testStart) & (df['synthetic_timestamp'] <= ranges.testEnd)]

    # Create copies to safely modify the data for serialization
    train_df_serializable = train_df.copy()
    test_df_serializable = test_df.copy()

    # Convert datetimes to JSON-safe ISO format strings
    train_df_serializable['synthetic_timestamp'] = train_df_serializable['synthetic_timestamp'].apply(lambda dt: dt.isoformat())
    test_df_serializable['synthetic_timestamp'] = test_df_serializable['synthetic_timestamp'].apply(lambda dt: dt.isoformat())

    # --- THIS IS THE FINAL FIX ---
    # Replace infinite values (Infinity, -Infinity) with NaN (Not a Number)
    # The JSON encoder cannot handle 'inf'.
    train_df_serializable.replace([np.inf, -np.inf], np.nan, inplace=True)
    test_df_serializable.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Now, when we convert to dict, Pandas will correctly handle NaN by converting
    # it to 'null', which IS a valid JSON value.
    train_data = train_df_serializable.to_dict(orient='records')
    test_data = test_df_serializable.to_dict(orient='records')
    # ---------------------------

    payload = {"train_data": train_data, "test_data": test_data}

    # Set a long timeout to allow for model training
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(f"{ML_SERVICE_URL}/train", json=payload)
            response.raise_for_status() # This will raise an exception for 4xx or 5xx responses
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Could not connect to ML service: {e}")
        except httpx.HTTPStatusError as e:
            # Re-raise the error from the ML service with more context
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from ML service: {e.response.text}")