# FILE: backend/app/routers/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
from app.datastore import mem_store

router = APIRouter()

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV file: {e}")

    if 'Response' not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain a 'Response' column.")

    # --- THIS IS THE CORRECTED PART ---
    # Create a timezone-AWARE timestamp in UTC. This will match the
    # timezone-aware datetimes coming from the frontend API.
    start_time = pd.Timestamp("2021-01-01 00:00:00", tz='UTC')
    df['synthetic_timestamp'] = start_time + pd.to_timedelta(df.index, unit='s')
    # ------------------------------------

    # Store DataFrame in memory
    mem_store['dataset'] = df
    if 'date_ranges' in mem_store:
        del mem_store['date_ranges']

    pass_count = df[df['Response'] == 0].shape[0]

    return {
        "totalRecords": len(df),
        "totalColumns": len(df.columns),
        "passRate": pass_count / len(df) if len(df) > 0 else 0,
        "dateRange": {
            "start": df['synthetic_timestamp'].min().isoformat(),
            "end": df['synthetic_timestamp'].max().isoformat()
        }
    }