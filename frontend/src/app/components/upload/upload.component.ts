import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

interface FileSummary {
  fileName: string;
  fileSize: string;
  columns: number;
  rows: number;
  missingValues: string;
  lastUpload: string;
}

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  selectedFile: File | null = null;
  fileSummary: FileSummary | null = null;
  isUploading = false;
  uploadSuccess = false;

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file && file.type === 'text/csv') {
      this.selectedFile = file;
      this.analyzeFile(file);
    }
  }

  private analyzeFile(file: File) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const csv = e.target.result;
      const lines = csv.split('\n');
      const headers = lines[0].split(',');
      
      // Calculate missing values (simplified)
      let missingCount = 0;
      for (let i = 1; i < Math.min(lines.length, 100); i++) {
        const values = lines[i].split(',');
        missingCount += values.filter((v: string) => !v || v.trim() === '').length;
      }
      const missingPercentage = ((missingCount / (headers.length * Math.min(lines.length - 1, 99))) * 100).toFixed(2);

      this.fileSummary = {
        fileName: file.name.length > 30 ? file.name.substring(0, 30) + '...' : file.name,
        fileSize: this.formatFileSize(file.size),
        columns: headers.length,
        rows: lines.length - 1,
        missingValues: missingPercentage + '%',
        lastUpload: new Date().toLocaleDateString()
      };
    };
    reader.readAsText(file);
  }

  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  async uploadFile() {
    if (!this.selectedFile || !this.fileSummary) return;

    this.isUploading = true;
    
    const formData = new FormData();
    formData.append('file', this.selectedFile);

    try {
      // Upload to backend
      const response = await this.http.post('http://localhost:8000/upload', formData).toPromise();
      console.log('Upload successful:', response);
      
      this.uploadSuccess = true;
      this.isUploading = false;
      
      // Navigate to next step after a short delay
      setTimeout(() => {
        this.router.navigate(['/mapping']);
      }, 1500);
      
    } catch (error) {
      console.error('Upload failed:', error);
      this.isUploading = false;
      // In a real app, show error message to user
    }
  }

  clearData() {
    this.selectedFile = null;
    this.fileSummary = null;
    this.uploadSuccess = false;
  }

  nextStep() {
    if (this.fileSummary) {
      this.router.navigate(['/mapping']);
    }
  }
}
