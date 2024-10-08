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
import { ApiService } from '../api/api.service';

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
  constructor(private apiService: ApiService) {}
  @Input() reconnecting!: boolean;

  @Output() hostGameEvent = new EventEmitter<object>();

  username: string = '';
  roomCode: string = '';
  showPopup: boolean = false;
  errorMessage: string = '';
  popupTimeout: any;

  logoUrl = '/assets/img/trivial.png';
  logoBackdropUrl = '/assets/img/question.gif';
  mainMusicUrl = '/assets/audio/trivial_music.mp3';

  clickedJoinGame: boolean = false;

  buttonClicked: boolean = false;

  ngAfterViewInit() {
    this.buttonClicked = false;
  }

  onClickJoinGame() {
    this.clickedJoinGame = true;
  }

  showError(error: string) {
    this.errorMessage = error;
    this.showPopup = true;
    this.popupTimeout = setTimeout(() => {
      this.showPopup = false;
    }, 3000);
  }

  onClickJoin(): void {
    clearTimeout(this.popupTimeout);
    if (!this.username.trim()) {
      this.showError('Please enter a username first!');
    } else if (!this.roomCode.trim()) {
      this.showError('Please enter a valid room code!');
    } else {
      if (this.buttonClicked) {
        return;
      }
      this.buttonClicked = true;

      this.apiService.validRoom(this.roomCode).subscribe({
        next: (value) => {
          if (value) {
            this.errorMessage = '';
            this.showPopup = false;
            this.hostGameEvent.emit({
              state: PageStates.Waiting,
              roomId: this.roomCode.trim(),
              host: false,
              username: this.username,
            });
          } else {
            this.showError('A room with that code does not exist!');
          }
        },
      });
    }
  }

  onClickHostGame(): void {
    clearTimeout(this.popupTimeout);
    if (!this.username.trim()) {
      this.showError('Please enter a username first!');
    } else {
      if (this.buttonClicked && !this.reconnecting) {
        return;
      }
      this.buttonClicked = true;

      this.errorMessage = '';
      this.showPopup = false;
      this.apiService.createRoomId().subscribe({
        next: (v) => {
          this.hostGameEvent.emit({
            state: PageStates.Waiting,
            roomId: v.room_id,
            host: true,
            username: this.username,
          });
        },
        error: (e) => {
          console.error('Error creating room id:', e);
          this.buttonClicked = false;
        }
      });
    }
  }

  onClickAbout() {
    this.hostGameEvent.emit({ state: PageStates.About });
  }
}
