from pydantic import BaseModel
from datetime import datetime

class DateRangePayload(BaseModel):
    trainStart: datetime
    trainEnd: datetime
    testStart: datetime
    testEnd: datetime
    simStart: datetime
    simEnd: datetime

class TrainingPayload(BaseModel):
    train_data: list
    test_data: list