import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  HostListener,
  Input,
  Output,
  QueryList,
  ViewChild,
  ViewChildren,
} from '@angular/core';
import { CommonModule, NgOptimizedImage } from '@angular/common';
import { Clipboard } from '@angular/cdk/clipboard';
import { PageStates } from '../app.component';
import { Category, WaitingTaglist } from './waiting_taglist.component';
import { MatTooltip, MatTooltipModule } from '@angular/material/tooltip';
import { LoadingComponent } from './loading.component';
import { PlayersListComponent } from './player_list.component';
import { Player } from '../api/GameData';

@Component({
  selector: 'waiting-view',
  standalone: true,
  imports: [
    NgOptimizedImage,
    CommonModule,
    WaitingTaglist,
    MatTooltipModule,
    LoadingComponent,
    PlayersListComponent,
  ],
  templateUrl: '../components_html/waiting.component.html',
  styleUrl: '../components_css/waiting.component.css',
})
export class WaitingComponent implements AfterViewInit {
  constructor(private clipboard: Clipboard) {}
  @Input() bgOverlay!: ElementRef;
  @Input() roomId!: string;
  // @Input() players!: Array<Record<string, string>>;
  @Input() players!: Player[];
  @Input() isHost!: boolean;

  @Output() hostGameEvent = new EventEmitter<object>();
  @ViewChild('tooltip') tooltip!: MatTooltip;

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
    this.hostGameEvent.emit({ state: PageStates.Landing });
  }
  onClickRoomCode() {
    this.tooltip.show();
    this.clipboard.copy(this.roomId);
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

  onClickStartGame() {
    this.hostGameEvent.emit({
      state: PageStates.Loading,
      numClues: this.numQuestions,
      numCategories: this.numCategories,
      loadingMessage:
        '<b>Hang tight!</b> Generating your clues. This may take a while.',
    });
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
