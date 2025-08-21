import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

interface DateRange {
  startDate: string;
  endDate: string;
  days: number;
}

@Component({
  selector: 'app-data-mapping',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './data-mapping.component.html',
  styleUrls: ['./data-mapping.component.scss']
})
export class DataMappingComponent {
  trainingPeriod: DateRange = { startDate: '2023-01-01', endDate: '2023-08-31', days: 243 };
  testingPeriod: DateRange = { startDate: '2023-09-01', endDate: '2023-10-31', days: 61 };
  simulationPeriod: DateRange = { startDate: '2023-11-01', endDate: '2023-12-31', days: 61 };
  isValidationSuccess = false;

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  onDateChange() {
    this.calculateDays();
  }

  private calculateDays() {
    this.trainingPeriod.days = this.getDaysBetween(this.trainingPeriod.startDate, this.trainingPeriod.endDate);
    this.testingPeriod.days = this.getDaysBetween(this.testingPeriod.startDate, this.testingPeriod.endDate);
    this.simulationPeriod.days = this.getDaysBetween(this.simulationPeriod.startDate, this.simulationPeriod.endDate);
  }

  private getDaysBetween(startDate: string, endDate: string): number {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  validateRanges() {
    // Simple validation: check if dates are in chronological order
    const trainingEnd = new Date(this.trainingPeriod.endDate);
    const testingStart = new Date(this.testingPeriod.startDate);
    const testingEnd = new Date(this.testingPeriod.endDate);
    const simulationStart = new Date(this.simulationPeriod.startDate);

    if (trainingEnd < testingStart && testingEnd < simulationStart) {
      this.isValidationSuccess = true;
      this.sendDateRanges();
    } else {
      this.isValidationSuccess = false;
    }
  }

  private async sendDateRanges() {
    try {
      const dateRanges = {
        training: this.trainingPeriod,
        testing: this.testingPeriod,
        simulation: this.simulationPeriod
      };
      const response = await this.http.post('http://localhost:8000/date-ranges', dateRanges).toPromise();
      console.log('Date ranges saved:', response);
    } catch (error) {
      console.error('Failed to save date ranges:', error);
    }
  }

  nextStep() {
    if (this.isValidationSuccess) {
      this.router.navigate(['/training']);
    }
  }
}
