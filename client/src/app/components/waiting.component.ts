import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  Output,
  ViewChild,
} from '@angular/core';
import { CommonModule, NgOptimizedImage } from '@angular/common';
import { Clipboard } from '@angular/cdk/clipboard';
import { PageStates } from '../app.component';
import { Category, WaitingTaglist } from './waiting_taglist.component';
import { MatTooltip, MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'waiting-view',
  standalone: true,
  imports: [NgOptimizedImage, CommonModule, WaitingTaglist, MatTooltipModule],
  templateUrl: '../components_html/waiting.component.html',
  styleUrl: '../components_css/waiting.component.css',
})
export class WaitingComponent implements AfterViewInit {
  constructor(private clipboard: Clipboard) {}
  @Input() bgOverlay!: ElementRef;
  @Output() hostGameEvent = new EventEmitter<PageStates>();
  @ViewChild('tooltip') tooltip!: MatTooltip;

  isHost = true; // temp isHost var
  roomCode = '1LOVML'; // temp roomCode var
  roomCodeTooltip = 'Copy to clipboard';

  logoUrl = '/assets/img/trivial.png';
  logoBackdropUrl = '/assets/img/question.gif';

  categories: Category[] = [
    { name: 'Science' },
    { name: 'History' },
    { name: 'Literature' },
  ];

  numCategories = 6;
  numQuestions = 5;

  minNumCategories = 1;
  minNumQuestions = 1;

  maxNumCategories = 12;
  maxNumQuestions = 10;

  ngAfterViewInit() {
    setTimeout(() => {
      this.bgOverlay.nativeElement.classList.add('bg-rendered');
    }, 10);
  }

  onClickLeaveGame() {
    this.hostGameEvent.emit(PageStates.Landing);
  }
  onClickRoomCode() {
    this.tooltip.show();
    this.clipboard.copy(this.roomCode);
    this.updateRoomCodeTooltip(false);
    setTimeout(() => this.tooltip.hide(1500));
  }

  setNumCategories(num: string) {
    this.numCategories = parseInt(num);
  }
  setNumQuestions(num: string) {
    this.numQuestions = parseInt(num);
  }

  updateRoomCodeTooltip(reset: boolean) {
    this.roomCodeTooltip = reset ? 'Copy to clipboard' : 'Copied!';
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
