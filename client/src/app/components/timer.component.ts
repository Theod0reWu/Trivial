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
  updateTimer(){
    const timerContainer = document.querySelector('.timer') as HTMLElement;
  }

  timerFraction = .5;
}