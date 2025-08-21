import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

interface TrainingMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
}

@Component({
  selector: 'app-model-training',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './model-training.component.html',
  styleUrls: ['./model-training.component.scss']
})
export class ModelTrainingComponent implements OnInit {
  isTraining = false;
  trainingProgress = 0;
  trainingComplete = false;
  
  metrics: TrainingMetrics = {
    accuracy: 94.2,
    precision: 92.8,
    recall: 91.5,
    f1Score: 92.1
  };

  trainingData = [
    { epoch: 0, accuracy: 0.65, loss: 120 },
    { epoch: 2, accuracy: 0.72, loss: 95 },
    { epoch: 4, accuracy: 0.78, loss: 75 },
    { epoch: 6, accuracy: 0.82, loss: 60 },
    { epoch: 8, accuracy: 0.86, loss: 45 },
    { epoch: 10, accuracy: 0.89, loss: 35 },
    { epoch: 12, accuracy: 0.91, loss: 28 },
    { epoch: 14, accuracy: 0.93, loss: 22 },
    { epoch: 16, accuracy: 0.94, loss: 18 },
    { epoch: 18, accuracy: 0.94, loss: 16 },
    { epoch: 20, accuracy: 0.94, loss: 15 }
  ];

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit() {
    // Auto-start training when component loads
    this.startTraining();
  }

  startTraining() {
    this.isTraining = true;
    this.trainingProgress = 0;
    this.trainingComplete = false;

    const interval = setInterval(() => {
      this.trainingProgress += 5;
      
      if (this.trainingProgress >= 100) {
        this.trainingProgress = 100;
        this.isTraining = false;
        this.trainingComplete = true;
        clearInterval(interval);
        
        // Send training completion to backend
        this.sendTrainingComplete();
      }
    }, 200);
  }

  stopTraining() {
    this.isTraining = false;
    // In a real app, this would send a stop signal to the backend
  }

  getAccuracyPoints(): string {
    return this.trainingData.map((point, index) => {
      const x = (index / (this.trainingData.length - 1)) * 400;
      const y = 200 - (point.accuracy * 200);
      return `${x},${y}`;
    }).join(' ');
  }

  getLossPoints(): string {
    return this.trainingData.map((point, index) => {
      const x = (index / (this.trainingData.length - 1)) * 400;
      const normalizedLoss = Math.min(point.loss / 120, 1); // Normalize to 0-1
      const y = 200 - (normalizedLoss * 200);
      return `${x},${y}`;
    }).join(' ');
  }

  private async sendTrainingComplete() {
    try {
      const response = await this.http.post('http://localhost:8000/training-complete', {
        metrics: this.metrics,
        trainingData: this.trainingData
      }).toPromise();
      console.log('Training completed:', response);
    } catch (error) {
      console.error('Failed to send training completion:', error);
    }
  }

  nextStep() {
    if (this.trainingComplete) {
      this.router.navigate(['/simulation']);
    }
  }
}
