import { Component, EventEmitter, Input, Output } from '@angular/core';
import { NgIf, NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { FormsModule } from '@angular/forms';
import {
  animate,
  state,
  style,
  transition,
  trigger,
} from '@angular/animations';

@Component({
  selector: 'landing-view',
  standalone: true,
  imports: [NgOptimizedImage, FormsModule, NgIf],
  templateUrl: '../components_html/landing.component.html',
  styleUrl: '../components_css/landing.component.css',
  animations: [
    trigger('fadeInOut', [
      state(
        'void',
        style({
          opacity: 0,
        })
      ),
      transition(':enter', [animate('0.25s', style({ opacity: 1 }))]),
      transition(':leave', [animate('0.25s', style({ opacity: 0 }))]),
    ]),
  ],
})
export class LandingComponent {
  @Output() hostGameEvent = new EventEmitter<PageStates>();
  username: string = '';
  roomCode: string = '';
  showPopup: boolean = false;
  errorMessage: string = '';
  popupTimeout: any;

  logoUrl = '/assets/img/trivial.png';
  logoBackdropUrl = '/assets/img/question.gif';
  mainMusicUrl = '/assets/audio/trivial_music.mp3';

  clickedJoinGame = false;

  onClickJoinGame() {
    this.clickedJoinGame = true;
  }

  onClickJoin() {
    clearTimeout(this.popupTimeout);
    if (!this.username.trim()) {
      this.errorMessage = 'Please enter a username first!';
      this.showPopup = true;
      this.popupTimeout = setTimeout(() => {
        this.showPopup = false;
      }, 3000);
    } else if (!this.roomCode.trim()) {
      this.errorMessage = 'Please enter a valid room code!';
      this.showPopup = true;
      this.popupTimeout = setTimeout(() => {
        this.showPopup = false;
      }, 3000);
    } else {
      this.errorMessage = '';
      this.showPopup = false;
      this.hostGameEvent.emit(PageStates.Waiting);
    }
  }

  onClickHostGame() {
    clearTimeout(this.popupTimeout);
    if (!this.username.trim()) {
      this.errorMessage = 'Please enter a username first!';
      this.showPopup = true;
      this.popupTimeout = setTimeout(() => {
        this.showPopup = false;
      }, 3000);
    } else {
      this.errorMessage = '';
      this.showPopup = false;
      this.hostGameEvent.emit(PageStates.Waiting);
    }
  }
}
