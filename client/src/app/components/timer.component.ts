import { 
  Component, 
  EventEmitter, 
  Input, 
  Output, 
  ViewChild, 
  ElementRef 
} from '@angular/core';
import { PageStates } from '../app.component';
import { NgClass, NgForOf } from '@angular/common';
import { Observable } from 'rxjs';

@Component({
  selector: 'timer',
  standalone: true,
  imports: [NgForOf, NgClass],
  templateUrl: '../components_html/timer.component.html',
  styleUrl: '../components_css/timer.component.css',
})
export class TimerComponent {
  // the current progress of the timer, goes from 0 (start) to 1 (end)
  @Input() onMessage$: Observable<any>;
  timerFraction = 0;
  start_time: number;
  interval: any;
  active = false;

  // keep these cutoff for each timer section to cover the same amount of time
  cutoffs = [0, .2, .4, .6, .8, .6, .4, .2, 0];

  // start and end colors of each timer module
  startColor = [235, 56, 56];
  endColor = [122, 114, 114];

  ngAfterViewInit(): void{
    this.onMessage$.subscribe({
      next: (value) => {
        if (value["action"] === "start") {
          this.start(value["duration"]);
        }
      }
    });
  }

  start(duration: number) {
    this.start_time = new Date().getTime();
    this.active = true;
    this.interval = setInterval(() => {
      let time = new Date().getTime();
      this.timerFraction = (time - this.start_time) / (1000 * duration);
      this.updateTimer();
    }, 15);

    setTimeout(() => {
      clearInterval(this.interval);
      this.active = false;
    }, duration * 1000);
  }

  stopNow() {
    this.active = false;
    clearInterval(this.interval);
  }

  updateTimer(){
    // const timerContainer = document.querySelector('.timer-container') as HTMLElement;
    const timerContainer = document.getElementById("timer-cont") as HTMLElement;
    if (!timerContainer){
      return;
    }
    for (var i = 0; i < 9; ++i){
      const child = timerContainer.children[i] as HTMLElement;

      var fraction = Math.min(Math.max((this.timerFraction - this.cutoffs[i]) / .2, 0), 1);
      var color = "rgb(" + Math.round(this.startColor[0] + (this.endColor[0] - this.startColor[0]) * fraction) + "," 
        + Math.round(this.startColor[1] + (this.endColor[1] - this.startColor[1]) * fraction) + "," 
        + Math.round(this.startColor[2] + (this.endColor[2] - this.startColor[2]) * fraction) + ")";
      child.style.setProperty("background-color", color);
    }
  }
}