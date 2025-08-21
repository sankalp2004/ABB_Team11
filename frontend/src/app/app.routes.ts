import { Routes } from '@angular/router';
import { UploadComponent } from './components/upload/upload.component';
import { DataMappingComponent } from './components/data-mapping/data-mapping.component';
import { ModelTrainingComponent } from './components/model-training/model-training.component';
import { SimulationComponent } from './components/simulation/simulation.component';

export const routes: Routes = [
  { path: '', redirectTo: '/upload', pathMatch: 'full' },
  { path: 'upload', component: UploadComponent },
  { path: 'mapping', component: DataMappingComponent },
  { path: 'training', component: ModelTrainingComponent },
  { path: 'simulation', component: SimulationComponent },
  { path: '**', redirectTo: '/upload' }
];
