import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  currentStep = 1;

  constructor(private router: Router) {}

  ngOnInit() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      this.updateCurrentStep(event.url);
    });
  }

  private updateCurrentStep(url: string) {
    if (url.includes('/upload')) {
      this.currentStep = 1;
    } else if (url.includes('/mapping')) {
      this.currentStep = 2;
    } else if (url.includes('/training')) {
      this.currentStep = 3;
    } else if (url.includes('/simulation')) {
      this.currentStep = 4;
    }
  }
}
