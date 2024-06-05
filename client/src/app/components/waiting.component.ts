import { AfterViewInit, Component, ElementRef, Input } from '@angular/core';
import { CommonModule, NgOptimizedImage } from '@angular/common';

@Component({
  selector: 'waiting-view',
  standalone: true,
  imports: [NgOptimizedImage, CommonModule],
  templateUrl: '../components_html/waiting.component.html',
  styleUrl: '../components_css/waiting.component.css',
})
export class WaitingComponent implements AfterViewInit {
  @Input() bgOverlay!: ElementRef;

  logoUrl = '/assets/img/trivial.png';
  logoBackdropUrl = '/assets/img/question.gif';

  ngAfterViewInit() {
    setTimeout(() => {
      this.bgOverlay.nativeElement.classList.add('bg-rendered');
    }, 10);
  }
  //   mainMusicUrl = '/assets/audio/trivial_music.mp3';

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
