import pandas as pd
import lightgbm as lgb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# --- 1. App & In-Memory Storage Initialization ---

app = FastAPI(
    title="IntelliInspect ML Service",
    description="A service for training a quality control model and making real-time predictions.",
    version="1.0.0"
)

# In-memory "database" to store the trained model and its metadata.
# In a production system, this would be a model registry (e.g., MLflow, S3).
model_storage = {}


# --- 2. Pydantic Models for Request & Response Validation ---

class TrainRequest(BaseModel):
    """Defines the expected JSON structure for a training request."""
    train_data: List[Dict[str, Any]]
    test_data: List[Dict[str, Any]]


class PredictRequest(BaseModel):
    """Defines the expected JSON structure for a prediction request."""
    data: Dict[str, Any]


class PredictResponse(BaseModel):
    """Defines the JSON response for a prediction."""
    prediction: str = Field(..., description="The prediction label, either 'Pass' or 'Fail'.")
    confidence: float = Field(..., description="The model's confidence in the prediction (0.0 to 1.0).")


# --- 3. API Endpoints ---

@app.get("/")
def read_root():
    """Root endpoint to confirm the service is running."""
    return {"status": "IntelliInspect ML Service is running."}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ml-service-python"}


@app.post("/train")
async def train_model(request: TrainRequest):
    """
    Trains a classification model, evaluates it, stores it in memory,
    and returns performance metrics.
    """
    if not request.train_data or not request.test_data:
        raise HTTPException(status_code=400, detail="Training and testing data cannot be empty.")

    try:
        train_df = pd.DataFrame(request.train_data)
        test_df = pd.DataFrame(request.test_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse data into DataFrame: {e}")

    # --- Feature Engineering & Data Preparation ---
    target = 'Response'
    # Exclude non-feature columns as per the spec. 'Id' is common in Kaggle datasets.
    cols_to_drop = [target, 'synthetic_timestamp', 'Id']

    features = [col for col in train_df.columns if col not in cols_to_drop]

    # Ensure all feature columns are present in both dataframes
    if not all(f in test_df.columns for f in features):
        raise HTTPException(status_code=400, detail="Test data is missing feature columns present in train data.")

    X_train = train_df[features]
    y_train = train_df[target].astype(int)

    X_test = test_df[features]
    y_test = test_df[target].astype(int)

    # --- Model Training ---
    # LightGBM is chosen for its speed and performance on tabular data.
    print("Starting model training...")
    lgbm = lgb.LGBMClassifier(objective='binary', random_state=42)
    lgbm.fit(X_train, y_train)
    print("Model training completed.")

    # --- Model Evaluation ---
    print("Evaluating model...")
    y_pred = lgbm.predict(X_test)

    # Calculate metrics as required by the specification
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    # Calculate confusion matrix: TN, FP, FN, TP
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    # --- Store Model in Memory ---
    # We store the model and the feature list to ensure consistency during prediction.
    model_storage['model'] = lgbm
    model_storage['features'] = features
    print("Model and features stored successfully.")

    return {
        "status": "Model Trained Successfully",
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        },
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        }
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Makes a prediction for a single data row using the trained model.
    """
    if 'model' not in model_storage:
        raise HTTPException(status_code=404,
                            detail="Model not found. Please train a model first via the /train endpoint.")

    model = model_storage['model']
    features = model_storage['features']

    try:
        # Create a DataFrame from the single row of data
        inference_df = pd.DataFrame([request.data])
        # Ensure the column order and selection match the training data exactly
        inference_df = inference_df[features]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Input data is missing an expected feature column: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing input data: {e}")

    # Get prediction probabilities to calculate confidence
    pred_proba = model.predict_proba(inference_df)
    confidence = pred_proba.max()

    # Get the class prediction (0 or 1)
    prediction_val = model.predict(inference_df)[0]

    # Map the numeric prediction to the required "Pass"/"Fail" label
    # As per the Kaggle dataset, 0 = No Failure (Pass), 1 = Failure (Fail)
    prediction_label = "Pass" if prediction_val == 0 else "Fail"

    return PredictResponse(
        prediction=prediction_label,
        confidence=float(confidence)
    )