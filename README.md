# MiniML - Predictive Quality Control System

A comprehensive machine learning application for predictive quality control with real-time simulation capabilities, built using Angular 18+, FastAPI, and Python ML services.

## 🏗️ System Architecture

### High-Level Overview
```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐    HTTP    ┌─────────────────┐
│   Angular 18+   │ ◄──────────────────► │   FastAPI       │ ◄────────► │   Python ML     │
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

Backend (FastAPI)
├── Upload Router (File handling)
├── Training Router (Model training coordination)
├── Simulation Router (Real-time simulation)
└── WebSocket Manager (Real-time communication)

ML Service (Python)
├── Model Training (LightGBM)
├── Prediction Engine
└── Performance Metrics
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Angular CLI (install globally: `npm install -g @angular/cli`)
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
   # Start FastAPI Backend
   cd backend
   pip install -r requirements.txt
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Start ML Service (in another terminal)
   cd ml-service-python
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

3. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npx ng serve
   ```

4. **Access the Application**
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:8000
   - ML Service: http://localhost:8001
   - API Documentation: http://localhost:8000/docs

### Docker Deployment
```bash
# Build and run all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
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
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── routers/                 # API endpoints
│   │   │   ├── upload.py            # File upload handling
│   │   │   ├── training.py          # Training coordination
│   │   │   └── simulation.py        # Simulation management
│   │   ├── main.py                  # FastAPI application
│   │   ├── models.py                # Data models
│   │   └── websocket_manager.py     # Real-time communication
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

#### Angular CLI Commands
```bash
# Development server
npx ng serve                    # Start development server (port 4200)
npx ng serve --host 0.0.0.0    # Allow external connections
npx ng serve --port 4200       # Specify custom port

# Build commands
npx ng build                   # Production build
npx ng build --watch           # Watch mode for development
npx ng build --configuration production  # Production configuration

# Testing
npx ng test                    # Run unit tests
npx ng e2e                     # Run end-to-end tests

# Code generation
npx ng generate component      # Generate new component
npx ng generate service        # Generate new service
npx ng generate pipe           # Generate new pipe
```

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

### Backend (FastAPI)

#### Key Technologies
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **WebSockets**: Real-time bidirectional communication
- **CORS**: Cross-origin resource sharing
- **In-memory storage**: Temporary data persistence

#### API Structure
```python
# Modular router pattern
app.include_router(upload.router, tags=["Upload"])
app.include_router(training.router, tags=["Training"])
app.include_router(simulation.router, tags=["Simulation"])
```

#### Data Flow
1. **Request Validation**: Pydantic models ensure data integrity
2. **Business Logic**: Process requests and coordinate with ML service
3. **Response Formatting**: Consistent JSON responses
4. **Error Handling**: Comprehensive error management

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
- `POST /upload` - Upload CSV file
- `GET /files` - List uploaded files
- `DELETE /files/{file_id}` - Delete uploaded file

#### Training Endpoints
- `POST /date-ranges` - Set training/testing/simulation periods
- `POST /training-complete` - Mark training as complete

#### Simulation Endpoints
- `POST /simulation/start` - Start real-time simulation
- `POST /simulation/stop` - Stop simulation
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

# Backend: Python FastAPI with optimized dependencies
FROM python:3.11-slim
# ... setup steps

# ML Service: Python ML environment with scientific libraries
FROM python:3.11-slim
# ... ML-specific setup
```

### Service Orchestration
```yaml
# docker-compose.yml
services:
  frontend-angular:    # Angular app on port 3000
  backend-dotnet:      # FastAPI on port 8000
  ml-service-python:   # ML service on port 8001
```

## 🔒 Security Features

### Frontend Security
- **CORS Configuration**: Proper cross-origin handling
- **Input Validation**: Client-side data validation
- **XSS Prevention**: Angular's built-in XSS protection

### Backend Security
- **Request Validation**: Pydantic model validation
- **CORS Middleware**: Controlled cross-origin access
- **Error Handling**: Secure error responses

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
npx ng serve       # Frontend (port 4200)
uvicorn backend.app.main:app --reload  # Backend (port 8000)
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
PYTHONPATH=/app
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
3. **Angular CLI not found**: Install globally with `npm install -g @angular/cli`
4. **Build errors**: Check TypeScript compilation errors
5. **API errors**: Verify backend service is running

#### Debug Mode
```bash
# Frontend debug
npx ng build --verbose

# Backend debug
uvicorn backend.app.main:app --reload --log-level debug

# ML Service debug
uvicorn main:app --reload --log-level debug
```

### Getting Help
- **Documentation**: Check this README and DESIGN.md
- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub discussions for questions

---

**MiniML - Predictive Quality Control System**  
Built with ❤️ using Angular 18+, FastAPI, and Python ML

## 👨‍💻 **Developed By**

- **Sankalp Jain** - Full Stack Development & System Architecture
- **Achyuth Samavedhi** - Backend Development & API Design  
- **Vineet Anand Modi** - Frontend Development & UI/UX Design

---

*This project demonstrates a complete machine learning pipeline from data ingestion to real-time prediction, showcasing modern web development practices and enterprise-grade architecture.*
