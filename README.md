# MiniML - Predictive Quality Control System

A comprehensive machine learning application for predictive quality control with real-time simulation capabilities, built using Angular 18+, ASP.NET 8, and Python ML services.

## 🏗️ System Architecture

### High-Level Overview
```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐    HTTP    ┌─────────────────┐
│   Angular 18+   │ ◄──────────────────► │   ASP.NET 8     │ ◄────────► │   Python ML     │
│   Frontend      │                      │   Backend       │            │   Service       │
│   (Port 4200)   │                      │   (Port 8000)   │            │   (Port 8001)   │
└─────────────────┘                      └─────────────────┘            └─────────────────┘
```

### Component Architecture
```
Frontend (Angular 18+)
├── App Component (Main Layout)
├── Upload Component (Step 1)
├── Data Mapping Component (Step 2)
├── Model Training Component (Step 3)
└── Simulation Component (Step 4)

Backend (ASP.NET 8)
├── Upload Endpoints (File handling)
├── Training Endpoints (Model training coordination)
├── Simulation Endpoints (Real-time simulation)
└── WebSocket Manager (Real-time communication)

ML Service (Python)
├── Model Training (LightGBM)
├── Prediction Engine
└── Performance Metrics
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Docker and Docker Compose (for containerized deployment)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd miniml-quality-control
   ```

2. **Start Backend Services**
   ```bash
   # Start ASP.NET 8 Backend
   cd backend
   dotnet run --urls "http://0.0.0.0:8000"
   
   # Start ML Service (in another terminal)
   cd ml-service-python
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

3. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Access the Application**
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:8000
   - ML Service: http://localhost:8001

### Docker Deployment
```bash
# Build and run all services
docker compose up -d --build backend-dotnet

# Access the application
# Frontend: http://localhost:4200
# Backend: http://localhost:8000
# ML Service: http://localhost:8001
```

## 📁 Project Structure

```
miniml-quality-control/
├── frontend/                          # Angular 18+ Frontend
│   ├── src/app/
│   │   ├── components/               # UI Components
│   │   │   ├── upload/              # File upload interface
│   │   │   ├── data-mapping/        # Date range configuration
│   │   │   ├── model-training/      # Training progress & metrics
│   │   │   └── simulation/          # Real-time prediction simulation
│   │   ├── app.component.*          # Main application layout
│   │   ├── app.routes.ts            # Angular routing
│   │   └── app.config.ts            # Application configuration
│   ├── Dockerfile                    # Frontend container
│   └── nginx.conf                    # Nginx configuration
├── backend/                          # ASP.NET 8 Backend
│   ├── Program.cs                   # Main application entry point
│   ├── MiniML.Backend.csproj        # Project configuration
│   └── Dockerfile                   # Backend container
├── ml-service-python/               # Python ML Service
│   ├── main.py                      # ML training & prediction
│   └── Dockerfile                   # ML service container
├── docker-compose.yml               # Multi-service orchestration
├── README.md                        # This file
└── DESIGN.md                        # Detailed design document
```

## 🔄 Application Flow

### 1. Data Upload (Step 1)
- **Frontend**: File selection and validation
- **Backend**: File storage and metadata extraction
- **Features**: CSV parsing, file size validation, column analysis

### 2. Data Mapping (Step 2)
- **Frontend**: Date range selection for training/testing/simulation
- **Backend**: Date range validation and storage
- **Features**: Chronological validation, duration calculation

### 3. Model Training (Step 3)
- **Frontend**: Training progress visualization
- **Backend**: Training coordination with ML service
- **ML Service**: LightGBM model training and evaluation
- **Features**: Real-time progress updates, performance metrics

### 4. Real-time Simulation (Step 4)
- **Frontend**: Live prediction dashboard
- **Backend**: Simulation orchestration and WebSocket management
- **ML Service**: Real-time predictions
- **Features**: Live metrics, prediction history, quality trends

## 🛠️ Technical Implementation

### Frontend (Angular 18+)

#### Key Technologies
- **Angular 18+**: Latest Angular framework with standalone components
- **TypeScript**: Type-safe JavaScript development
- **SCSS**: Advanced CSS preprocessing
- **Angular Router**: Client-side navigation
- **HttpClient**: HTTP communication with backend
- **WebSocket**: Real-time communication

#### Component Architecture
```typescript
// Standalone component pattern
@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  // Component logic
}
```

#### State Management
- **Component-level state**: Each component manages its own state
- **Service communication**: HTTP calls to backend for data persistence
- **Real-time updates**: WebSocket connections for live data

### Backend (ASP.NET 8)

#### Key Technologies
- **ASP.NET 8**: Modern .NET web framework with minimal APIs
- **System.Text.Json**: Data serialization and validation
- **WebSockets**: Real-time bidirectional communication
- **CORS**: Cross-origin resource sharing
- **In-memory storage**: Temporary data persistence with thread-safe collections

#### API Structure
```csharp
// Minimal API pattern with endpoint groups
app.MapPost("/upload", async (HttpRequest request, UploadedFilesStore store) => { ... });
app.MapPost("/date-ranges", async (HttpRequest req, TrainingStateStore store) => { ... });
app.MapPost("/simulation/start", (SimulationStateStore store) => { ... });
```

#### Data Flow
1. **Request Validation**: JSON deserialization with error handling
2. **Business Logic**: Process requests and coordinate with ML service
3. **Response Formatting**: Consistent JSON responses using Results.Json
4. **Error Handling**: Comprehensive error management with proper HTTP status codes

### ML Service (Python)

#### Key Technologies
- **LightGBM**: Gradient boosting framework for ML
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Machine learning utilities
- **FastAPI**: RESTful API for ML operations

#### Model Pipeline
```python
# Training pipeline
lgbm = lgb.LGBMClassifier(objective='binary', random_state=42)
lgbm.fit(X_train, y_train)

# Prediction pipeline
prediction = lgbm.predict(data)
confidence = lgbm.predict_proba(data)
```

## 🔌 API Endpoints

### Backend API (Port 8000)

#### Upload Endpoints
- `POST /upload` - Upload CSV file (supports up to 100MB)
- `GET /files` - List uploaded files
- `DELETE /files/{filename}` - Delete uploaded file

#### Training Endpoints
- `POST /date-ranges` - Set training/testing/simulation periods
- `GET /date-ranges` - Get saved date ranges
- `POST /training-complete` - Mark training as complete
- `GET /training-status` - Get current training status
- `POST /start-training` - Start training process
- `POST /stop-training` - Stop training process

#### Simulation Endpoints
- `POST /simulation/start` - Start real-time simulation
- `POST /simulation/stop` - Stop simulation
- `GET /simulation/status` - Get simulation status
- `GET /simulation/predictions` - Get all predictions
- `WebSocket /ws/simulation` - Real-time simulation data

### ML Service API (Port 8001)

#### Training Endpoints
- `POST /train` - Train ML model with provided data
- `GET /model/status` - Get model training status

#### Prediction Endpoints
- `POST /predict` - Make predictions on new data
- `GET /metrics` - Get model performance metrics

## 🐳 Docker Configuration

### Multi-Stage Builds
```dockerfile
# Frontend: Build Angular app and serve with Nginx
FROM node:18 AS builder
# ... build steps
FROM nginx:alpine AS production

# Backend: ASP.NET 8 with optimized runtime
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
# ... build steps
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
# ... runtime setup

# ML Service: Python ML environment with scientific libraries
FROM python:3.11-slim
# ... ML-specific setup
```

### Service Orchestration
```yaml
# docker-compose.yml
services:
  frontend-angular:    # Angular app on port 4200
  backend-dotnet:      # ASP.NET 8 on port 8000
  ml-service-python:   # ML service on port 8001
```

## 🔒 Security Features

### Frontend Security
- **CORS Configuration**: Proper cross-origin handling
- **Input Validation**: Client-side data validation
- **XSS Prevention**: Angular's built-in XSS protection

### Backend Security
- **Request Validation**: JSON model validation with error handling
- **CORS Middleware**: Controlled cross-origin access
- **Error Handling**: Secure error responses with proper HTTP status codes
- **File Upload Limits**: Configurable file size limits (100MB default)

### ML Service Security
- **Input Sanitization**: Data validation before processing
- **Model Isolation**: Secure model storage and access

## 📊 Performance Optimization

### Frontend Optimization
- **Lazy Loading**: Component-based code splitting
- **Angular Universal**: Server-side rendering support
- **Bundle Optimization**: Tree shaking and minification

### Backend Optimization
- **Async Operations**: Non-blocking I/O operations
- **Connection Pooling**: Efficient database connections
- **Caching**: In-memory data caching

### ML Service Optimization
- **Model Caching**: Trained model persistence
- **Batch Processing**: Efficient data processing
- **Memory Management**: Optimized memory usage

## 🧪 Testing Strategy

### Frontend Testing
- **Unit Tests**: Component and service testing
- **E2E Tests**: End-to-end user flow testing
- **Integration Tests**: API integration testing

### Backend Testing
- **API Tests**: Endpoint functionality testing
- **Unit Tests**: Business logic testing
- **Integration Tests**: Service integration testing

### ML Service Testing
- **Model Tests**: Model accuracy and performance testing
- **API Tests**: Prediction endpoint testing
- **Data Tests**: Data validation and processing testing

## 📈 Monitoring and Logging

### Application Monitoring
- **Health Checks**: Service health monitoring
- **Performance Metrics**: Response time and throughput
- **Error Tracking**: Comprehensive error logging

### ML Model Monitoring
- **Model Performance**: Accuracy and drift monitoring
- **Prediction Logging**: Prediction history and analysis
- **Data Quality**: Input data validation and monitoring

## 🚀 Deployment

### Development Environment
```bash
# Local development setup
npm start          # Frontend (port 4200)
dotnet run --urls "http://0.0.0.0:8000"  # Backend (port 8000)
uvicorn main:app --reload              # ML Service (port 8001)
```

### Production Environment
```bash
# Docker deployment
docker-compose up --build -d

# Environment variables
NODE_ENV=production
PYTHONPATH=/app
ML_SERVICE_URL=http://ml-service-python:8000
```

## 🔧 Configuration

### Environment Variables
```bash
# Frontend
NODE_ENV=production
API_BASE_URL=http://localhost:8000

# Backend
ASPNETCORE_URLS=http://+:8000
ML_SERVICE_URL=http://ml-service-python:8000
CORS_ORIGINS=http://localhost:4200,http://localhost:3000

# ML Service
PYTHONPATH=/app
MODEL_STORAGE_PATH=/app/models
```

### Configuration Files
- `angular.json` - Angular build configuration
- `tsconfig.json` - TypeScript configuration
- `nginx.conf` - Nginx server configuration
- `docker-compose.yml` - Service orchestration

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes**: Follow coding standards and add tests
4. **Test thoroughly**: Run all tests and verify functionality
5. **Submit pull request**: Detailed description of changes

### Code Standards
- **TypeScript**: Strict type checking enabled
- **Python**: PEP 8 style guide
- **Angular**: Angular style guide compliance
- **Documentation**: Comprehensive code documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Troubleshooting

#### Common Issues
1. **Port conflicts**: Ensure ports 4200, 8000, 8001 are available
2. **Dependency issues**: Clear node_modules and reinstall
3. **Build errors**: Check TypeScript compilation errors
4. **API errors**: Verify backend service is running

#### Debug Mode
```bash
# Frontend debug
npm run build --verbose

# Backend debug
dotnet run --urls "http://0.0.0.0:8000" --verbosity detailed

# ML Service debug
uvicorn main:app --reload --log-level debug
```

### Getting Help
- **Documentation**: Check this README and DESIGN.md
- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub discussions for questions

---

**MiniML - Predictive Quality Control System**  
Built by Sankalp, Achyuth and Vineet
