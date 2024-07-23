import { Component, EventEmitter, Input, Output } from '@angular/core';
import { PageStates } from '../app.component';
import { NgClass, NgForOf } from '@angular/common';

@Component({
  selector: 'timer',
  standalone: true,
  imports: [NgForOf, NgClass],
  templateUrl: '../components_html/timer.component.html',
  styleUrl: '../components_css/timer.component.css',
})
export class TimerComponent {
  // the current progress of the timer, goes from 0 (start) to 1 (end)
  timerFraction = 0;

  // keep these cutoff for each timer section to cover the same amount of time
  cutoffs = [0, .2, .4, .6, .8, .6, .4, .2, 0];

  // start and end colors of each timer module
  startColor = [235, 56, 56];
  endColor = [122, 114, 114];

  updateTimer(){
    const timerContainer = document.querySelector('.timer') as HTMLElement;

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