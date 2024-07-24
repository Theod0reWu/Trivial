import { Component, EventEmitter, Input, Output } from '@angular/core';
// import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { NgClass, NgForOf, CommonModule } from '@angular/common';
import { Player } from '../api/GameData';
import { TimerComponent } from './timer.component';

enum BannerStates {
  Empty = "empty",
  Green = "green",
  Red = "red",
  AltAnswering = "altanswering",
  Answering = "answering"
}

@Component({
  selector: 'clue-view',
  standalone: true,
  imports: [NgForOf, NgClass, CommonModule, TimerComponent],
  templateUrl: '../components_html/clue.component.html',
  styleUrl: '../components_css/clue.component.css',
})
export class ClueComponent {
  @Input() players!: Player[];
  @Input() scores!: number[];
  @Input() clue!: string;
  @Output() gameStateChange = new EventEmitter<boolean>();

  progress: number = 0;
  start_time: number;
  progress_interval: any;

  startProgressBar(duration: number): void {
    this.start_time = new Date().getTime();

    this.progress_interval = setInterval(() => {
      let time = new Date().getTime();
      this.progress = (time - this.start_time) / (1000 * duration);
    }, 17);

    setTimeout(() => {
      clearInterval(this.progress_interval);
    }, duration * 1000);
  }

  updateTimer(){
    const timerContainer = document.querySelector('.timer') as HTMLElement;
  }
  
  BannerType = BannerStates
  banner = BannerStates.AltAnswering;

  bannerText = "Who/What is Berlin?";
  answeringText = "Team 1 is answering";

  timerFraction = .5;

}
