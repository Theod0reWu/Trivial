import { Component, EventEmitter, Input, Output } from '@angular/core';
import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';

@Component({
  selector: 'landing-view',
  standalone: true,
  imports: [NgOptimizedImage],
  templateUrl: '../components_html/landing.component.html',
  styleUrl: '../components_css/landing.component.css',
})
export class LandingComponent {
  @Output() hostGameEvent = new EventEmitter<PageStates>();

  logoUrl = '/assets/img/trivial.png';
  logoBackdropUrl = '/assets/img/question.gif';
  mainMusicUrl = '/assets/audio/trivial_music.mp3';

  clickedJoinGame = false;

  onClickJoinGame() {
    this.clickedJoinGame = true;
  }
  onClickHostGame() {
    this.hostGameEvent.emit(PageStates.Waiting);
  }
}
