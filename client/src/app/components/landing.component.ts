import { Component } from '@angular/core';
import { NgOptimizedImage } from '@angular/common';

@Component({
  selector: 'landing-view',
  standalone: true,
  imports: [NgOptimizedImage],
  templateUrl: '../components_html/landing.component.html',
  styleUrl: '../components_css/landing.component.css',
})
export class LandingComponent {
  logoUrl = '/assets/img/trivial.png';
  logoBackdropUrl = '/assets/img/question.gif';
}
