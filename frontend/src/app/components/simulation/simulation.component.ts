import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

interface Prediction {
  time: string;
  sampleId: string;
  prediction: string;
  confidence: number;
  computationTime: number;
  threshold: number;
  correct: boolean;
}

interface LiveStats {
  totalPredictions: number;
  outOfRange: number;
  accuracy: number;
}

@Component({
  selector: 'app-simulation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './simulation.component.html',
  styleUrls: ['./simulation.component.scss']
})
export class SimulationComponent implements OnInit, OnDestroy {
  isSimulationRunning = false;
  qualityScore = 85;
  confidence = 92;
  
  liveStats: LiveStats = {
    totalPredictions: 0,
    outOfRange: 0,
    accuracy: 0
  };

  predictions: Prediction[] = [];
  private simulationInterval: any;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    // Initialize with some sample data
    this.generateSamplePredictions();
  }

  ngOnDestroy() {
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
    }
  }

  startSimulation() {
    this.isSimulationRunning = true;
    this.liveStats.totalPredictions = 0;
    this.liveStats.outOfRange = 0;
    this.liveStats.accuracy = 0;
    this.predictions = [];

    // Start real-time simulation
    this.simulationInterval = setInterval(() => {
      this.generateNewPrediction();
      this.updateQualityScore();
      this.updateConfidence();
      this.updateStats();
    }, 2000);

    // Send start signal to backend
    this.sendSimulationStart();
  }

  stopSimulation() {
    this.isSimulationRunning = false;
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
    }
    
    // Send stop signal to backend
    this.sendSimulationStop();
  }

  private generateNewPrediction() {
    const now = new Date();
    const time = now.toLocaleTimeString();
    const sampleId = `SAMPLE-${Math.floor(Math.random() * 1000)}`;
    const prediction = Math.random() > 0.2 ? 'Pass' : 'Fail';
    const confidence = Math.floor(Math.random() * 20) + 80; // 80-100%
    const computationTime = Math.floor(Math.random() * 100) + 50; // 50-150ms
    const threshold = 85;
    const correct = Math.random() > 0.1; // 90% accuracy

    const newPrediction: Prediction = {
      time,
      sampleId,
      prediction,
      confidence,
      computationTime,
      threshold,
      correct
    };

    this.predictions.unshift(newPrediction);
    
    // Keep only last 20 predictions
    if (this.predictions.length > 20) {
      this.predictions = this.predictions.slice(0, 20);
    }
  }

  private updateQualityScore() {
    // Simulate fluctuating quality score
    const change = (Math.random() - 0.5) * 10;
    this.qualityScore = Math.max(60, Math.min(100, this.qualityScore + change));
  }

  private updateConfidence() {
    // Simulate fluctuating confidence
    const change = (Math.random() - 0.5) * 5;
    this.confidence = Math.max(80, Math.min(100, this.confidence + change));
  }

  private updateStats() {
    this.liveStats.totalPredictions++;
    
    if (this.predictions.length > 0) {
      const latest = this.predictions[0];
      if (latest.prediction === 'Fail') {
        this.liveStats.outOfRange++;
      }
      
      this.liveStats.accuracy = Math.round(
        (this.predictions.filter(p => p.correct).length / this.predictions.length) * 100
      );
    }
  }

  private generateSamplePredictions() {
    const sampleData = [
      { time: '12:00 PM', sampleId: 'SAMPLE-239', prediction: 'Pass', confidence: 91, computationTime: 89, threshold: 85, correct: true },
      { time: '12:01 PM', sampleId: 'SAMPLE-239', prediction: 'Pass', confidence: 90, computationTime: 92, threshold: 85, correct: true },
      { time: '12:02 PM', sampleId: 'SAMPLE-239', prediction: 'Pass', confidence: 89, computationTime: 87, threshold: 85, correct: true },
      { time: '12:03 PM', sampleId: 'SAMPLE-239', prediction: 'Pass', confidence: 92, computationTime: 94, threshold: 85, correct: true },
      { time: '12:04 PM', sampleId: 'SAMPLE-239', prediction: 'Pass', confidence: 88, computationTime: 91, threshold: 85, correct: true }
    ];

    this.predictions = sampleData.map(p => ({
      ...p,
      confidence: p.confidence,
      computationTime: p.computationTime
    }));
  }

  private async sendSimulationStart() {
    try {
      await this.http.post('http://localhost:8000/simulation/start', {}).toPromise();
      console.log('Simulation started');
    } catch (error) {
      console.error('Failed to start simulation:', error);
    }
  }

  private async sendSimulationStop() {
    try {
      await this.http.post('http://localhost:8000/simulation/stop', {}).toPromise();
      console.log('Simulation stopped');
    } catch (error) {
      console.error('Failed to stop simulation:', error);
    }
  }

  getQualityPoints(): string {
    // Generate quality trend points for the chart
    const points = [];
    for (let i = 0; i < 20; i++) {
      const x = (i / 19) * 400;
      const quality = 85 + Math.sin(i * 0.3) * 10 + (Math.random() - 0.5) * 5;
      const y = 200 - (quality / 100) * 200;
      points.push(`${x},${y}`);
    }
    return points.join(' ');
  }

  getQualityArea(): string {
    // Generate area fill points for the chart
    const points = this.getQualityPoints().split(' ');
    const areaPoints = [...points];
    
    // Add bottom corners to close the area
    areaPoints.push('400,200');
    areaPoints.push('0,200');
    
    return areaPoints.join(' ');
  }
}
