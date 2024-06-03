import { AfterViewInit, Component, ElementRef } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LandingComponent } from './components/landing.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, LandingComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements AfterViewInit {
  constructor(private elementRef: ElementRef) {}

  title = 'client';
  ngAfterViewInit() {
    this.elementRef.nativeElement.ownerDocument.body.style.background =
      'radial-gradient(closest-side, #CE79F6, #030084)';
  }
}
