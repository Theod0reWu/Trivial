import { AfterViewInit, Component, ElementRef, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LandingComponent } from './components/landing.component';
import { WaitingComponent } from './components/waiting.component';

export enum PageStates {
  Landing,
  About,
  Waiting,
  InGame,
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, LandingComponent, WaitingComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements AfterViewInit {
  constructor(private elementRef: ElementRef) {}
  @ViewChild('bg') bgOverlay!: ElementRef;
  pageStates = PageStates;
  title = 'client';

  state = this.pageStates.Landing;

  ngAfterViewInit() {
    this.elementRef.nativeElement.ownerDocument.body.style.background =
      'radial-gradient(closest-side, #CE79F6, #030084)';
    setTimeout(() => {
      this.bgOverlay.nativeElement.classList.remove('bg-rendered');
    }, 10);
    console.log(this.bgOverlay);
  }
  handleChangeState(state: PageStates) {
    if (state == PageStates.Waiting) {
      this.state = this.pageStates.Waiting;
      // this.elementRef.nativeElement.ownerDocument.body.style.background =
      //   'radial-gradient(ellipse 70vw 70vh, #CE79F6, #030084, #000000)';
    }
  }
}
