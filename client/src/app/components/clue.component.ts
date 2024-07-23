import { Component, EventEmitter, Input, Output } from '@angular/core';
// import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { NgClass, NgForOf } from '@angular/common';
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
  imports: [NgForOf, NgClass, TimerComponent],
  templateUrl: '../components_html/clue.component.html',
  styleUrl: '../components_css/clue.component.css',
})
export class ClueComponent {
  @Input() players!: Player[];
  @Input() scores!: number[];
  @Input() clue!: string;
  @Output() gameStateChange = new EventEmitter<boolean>();

  updateTimer(){
    const timerContainer = document.querySelector('.timer') as HTMLElement;
  }
  
  BannerType = BannerStates
  banner = BannerStates.AltAnswering;

  bannerText = "Who/What is Berlin?";
  answeringText = "Team 1 is answering";

  timerFraction = .5;

}
