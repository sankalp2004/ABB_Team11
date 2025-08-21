# MiniML - Predictive Quality Control - Design Document

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        MiniML Application                       │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Angular       │   ASP.NET 8     │   Python ML                │
│   Frontend      │   Backend       │   Service                   │
│   (Port 3000)   │   (Port 8000)   │   (Port 8001)              │
│                 │                 │                             │
│ • File Upload   │ • API Gateway   │ • Model Training           │
│ • Date Ranges   │ • Data Storage  │ • Predictions              │
│ • Training UI   │ • WebSocket     │ • Data Processing          │
│ • Simulation    │ • Orchestration │ • ML Algorithms            │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Angular)                      │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Upload        │   Data Mapping  │   Model Training           │
│   Component     │   Component     │   Component                │
│                 │                 │                             │
│ • File Analysis │ • Date Selection│ • Training Progress        │
│ • CSV Parsing   │ • Range Validation│ • Metrics Display        │
│ • Summary Cards │ • Chart Display │ • Performance Charts       │
└─────────────────┴─────────────────┴─────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Simulation Component                     │
│                                                                 │
│ • Real-Time Charts    • Live Statistics    • Prediction Stream │
│ • WebSocket Client    • Quality Metrics    • Confidence Display│
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow Diagram

### 1. Upload Flow
```
User → Frontend → Backend → File Storage
  ↓
File Analysis → Summary Cards → Next Step
```

### 2. Training Flow
```
Date Ranges → Backend → ML Service → Training
  ↓
Progress Updates → Frontend → Metrics Display
```

### 3. Simulation Flow
```
Start Simulation → Backend → ML Service → Predictions
  ↓
WebSocket → Frontend → Real-Time Charts
```

## 🔌 API Contract & Payload Structure

### 1. File Upload API

**Endpoint**: `POST /upload`

**Request**:
```http
Content-Type: multipart/form-data
Body: file (CSV)
```

**Response**:
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "filename": "dataset.csv",
    "file_size": 1024000,
    "rows": 1000,
    "columns": 50,
    "missing_values": "2.5%",
    "upload_time": "2023-12-01T10:30:00Z"
  }
}
```

### 2. Date Ranges API

**Endpoint**: `POST /date-ranges`

**Request**:
```json
{
  "training": {
    "startDate": "2023-01-01",
    "endDate": "2023-08-31",
    "days": 243
  },
  "testing": {
    "startDate": "2023-09-01",
    "endDate": "2023-10-31",
    "days": 61
  },
  "simulation": {
    "startDate": "2023-11-01",
    "endDate": "2023-12-31",
    "days": 61
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Date ranges saved successfully",
  "data": {
    "training": {...},
    "testing": {...},
    "simulation": {...},
    "saved_at": "2023-12-01T10:30:00Z"
  }
}
```

### 3. Training Complete API

**Endpoint**: `POST /training-complete`

**Request**:
```json
{
  "metrics": {
    "accuracy": 94.2,
    "precision": 92.8,
    "recall": 91.5,
    "f1Score": 92.1
  },
  "training_data": [
    {
      "epoch": 0,
      "accuracy": 0.65,
      "loss": 120
    }
  ]
}
```

### 4. Simulation WebSocket

**Connection**: `WS /ws/simulation`

**Message Format**:
```json
{
  "type": "prediction",
  "data": {
    "time": "12:00 PM",
    "sample_id": "SAMPLE-239",
    "prediction": "Pass",
    "confidence": 91,
    "computation_time": 89,
    "threshold": 85,
    "correct": true
  },
  "stats": {
    "total_predictions": 20,
    "out_of_range": 3,
    "accuracy": 85
  }
}
```

## 🗄️ Data Models

### File Summary Model
```typescript
interface FileSummary {
  fileName: string;
  fileSize: string;
  columns: number;
  rows: number;
  missingValues: string;
  lastUpload: string;
}
```

### Date Range Model
```typescript
interface DateRange {
  startDate: string;
  endDate: string;
  days: number;
}
```

### Training Metrics Model
```typescript
interface TrainingMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
}
```

### Prediction Model
```typescript
interface Prediction {
  time: string;
  sampleId: string;
  prediction: string;
  confidence: number;
  computationTime: number;
  threshold: number;
  correct: boolean;
}
```

## 🔄 State Management

### Frontend State
```typescript
interface AppState {
  currentStep: number;
  uploadedFile: FileSummary | null;
  dateRanges: {
    training: DateRange;
    testing: DateRange;
    simulation: DateRange;
  };
  trainingStatus: {
    isTraining: boolean;
    progress: number;
    metrics: TrainingMetrics | null;
  };
  simulationStatus: {
    isRunning: boolean;
    predictions: Prediction[];
    stats: LiveStats;
  };
}
```

### Backend State
```csharp
// In-memory storage with thread-safe collections (production: use database)
public sealed class UploadedFilesStore
{
    private readonly ConcurrentDictionary<string, UploadedFileInfo> fileNameToInfo = new();
}

public sealed class TrainingStateStore
{
    public Dictionary<string, object?> DateRanges { get; set; } = new();
    public TrainingState State { get; } = new();
}

public sealed class SimulationStateStore
{
    public SimulationState State { get; } = new();
}
```

## 🔒 Security Considerations

### 1. Input Validation
- File type validation (CSV only)
- File size limits
- Date range validation
- SQL injection prevention

### 2. CORS Configuration
```csharp
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
        policy.WithOrigins("http://localhost:4200", "http://localhost:3000")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials());
});
```

### 3. Docker Security
- Non-root containers
- Minimal base images
- Security headers in nginx
- Health checks

## 📈 Performance Considerations

### 1. Frontend Optimization
- Lazy loading of components
- Gzip compression
- Static asset caching
- Bundle optimization

### 2. Backend Optimization
- Async operations
- Connection pooling
- Efficient data serialization
- Memory management

### 3. ML Service Optimization
- Batch processing
- Model caching
- Efficient algorithms
- Resource monitoring

## 🧪 Testing Strategy

### 1. Unit Tests
- Component testing (Angular)
- API endpoint testing (FastAPI)
- ML algorithm testing (Python)

### 2. Integration Tests
- End-to-end workflow testing
- Service communication testing
- WebSocket testing

### 3. Performance Tests
- Load testing
- Stress testing
- Memory leak testing

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance benchmarks met
- [ ] Documentation updated

### Deployment
- [ ] Docker images built
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Health checks configured

### Post-Deployment
- [ ] Monitoring configured
- [ ] Logs verified
- [ ] Performance metrics checked
- [ ] User acceptance testing

## 🔍 Monitoring & Observability

### 1. Health Checks
- Service availability
- Response time monitoring
- Error rate tracking

### 2. Logging
- Structured logging
- Log aggregation
- Error tracking

### 3. Metrics
- Application metrics
- System metrics
- Business metrics

## 🚀 Future Enhancements

### 1. Advanced Features
- Model versioning
- A/B testing
- Feature importance visualization
- Automated retraining

### 2. Scalability
- Horizontal scaling
- Load balancing
- Database optimization
- Caching strategies

### 3. User Experience
- Dark mode
- Mobile optimization
- Accessibility improvements
- Internationalization

---

**Document Version**: 1.0  
**Last Updated**: August 2025  
**Author**: Achyuth Samavedhi, Sankalp Jain, Vineet Anand Modi
