import { AfterViewInit, Component, ElementRef, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LandingComponent } from './components/landing.component';
import { WaitingComponent } from './components/waiting.component';
import { BoardComponent } from './components/board.component';

export enum PageStates {
  Landing,
  About,
  Waiting,
  InGame,
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, LandingComponent, WaitingComponent, BoardComponent],
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
  }
  handleChangeState(state: PageStates) {
    switch (state) {
      case PageStates.Landing: {
        this.state = this.pageStates.Landing;
        setTimeout(() => {
          this.bgOverlay.nativeElement.classList.remove('bg-rendered');
        }, 10);
        break;
      }
      case PageStates.Waiting: {
        this.state = this.pageStates.Waiting;
        break;
      }
      case PageStates.InGame: {
        this.state = this.pageStates.InGame;
        break;
      }
    }
  }
}
