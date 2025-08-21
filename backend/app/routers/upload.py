# FILE: backend/app/routers/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
from datetime import datetime
from typing import Dict, Any

router = APIRouter()

# Store uploaded file info in memory (in production, use a database)
uploaded_files = {}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV file for analysis
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Read the file content
        content = await file.read()
        
        # Parse CSV to get basic info
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Calculate file statistics
        file_size = len(content)
        rows, columns = df.shape
        missing_values = df.isnull().sum().sum()
        missing_percentage = (missing_values / (rows * columns)) * 100 if rows * columns > 0 else 0
        
        # Store file info
        file_info = {
            "filename": file.filename,
            "file_size": file_size,
            "rows": rows,
            "columns": columns,
            "missing_values": missing_percentage,
            "upload_time": datetime.now().isoformat(),
            "content": content  # In production, save to file system or database
        }
        
        uploaded_files[file.filename] = file_info
        
        return JSONResponse({
            "success": True,
            "message": "File uploaded successfully",
            "data": {
                "filename": file.filename,
                "file_size": file_size,
                "rows": rows,
                "columns": columns,
                "missing_values": f"{missing_percentage:.2f}%",
                "upload_time": file_info["upload_time"]
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/files")
async def get_uploaded_files():
    """
    Get list of uploaded files
    """
    return {
        "files": [
            {
                "filename": info["filename"],
                "file_size": info["file_size"],
                "rows": info["rows"],
                "columns": info["columns"],
                "missing_values": f"{info['missing_values']:.2f}%",
                "upload_time": info["upload_time"]
            }
            for info in uploaded_files.values()
        ]
    }

@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    Delete an uploaded file
    """
    if filename in uploaded_files:
        del uploaded_files[filename]
        return {"success": True, "message": f"File {filename} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="File not found")