import { Component } from '@angular/core';
import { NgOptimizedImage } from '@angular/common';

@Component({
  selector: 'landing-view',
  standalone: true,
  imports: [NgOptimizedImage],
  templateUrl: '../components_html/landing.component.html',
  styleUrl: '../components_css/landing.component.css',
})
export class LandingComponent {
  logoUrl = '/assets/img/trivial.png';
  logoBackdropUrl = '/assets/img/question.gif';
  mainMusicUrl = '/assets/audio/trivial_music.mp3';

  clickedJoinGame = false;

  onClickJoinGame() {
    this.clickedJoinGame = true;
  }

  // private ensureAudioPlays(): void {
  //   const promise = this.audio.nativeElement.play();
  //   if (promise !== undefined) {
  //     promise
  //       .then(() => {
  //         // Autoplay started
  //       })
  //       .catch((error: any) => {
  //         // Autoplay was prevented.
  //         this.audio.nativeElement.muted = true;
  //         this.audio.nativeElement.play();
  //         console.error(error);
  //       });
  //   }
  // }
}
