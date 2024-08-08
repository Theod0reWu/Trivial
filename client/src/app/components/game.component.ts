import {
  Component,
  Input,
  Output,
  EventEmitter,
  ViewChild,
  ElementRef,
} from '@angular/core';
// import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { BoardComponent } from './board.component';
import { ClueComponent } from './clue.component';
import { FinalScoresComponent } from './final_scores.component';
import { Player, GameData } from '../api/GameData';
import { Observable, Subject, ReplaySubject } from 'rxjs';

@Component({
  selector: 'game-view',
  standalone: true,
  imports: [BoardComponent, ClueComponent, FinalScoresComponent],
  templateUrl: '../components_html/game.component.html',
})
export class GameComponent {
  @Input() numCols!: number;
  @Input() numRows!: number;
  @Input() categoryTitles!: string[];
  @Input() players!: Player[];
  @Input() isHost!: boolean;
  @Input() prices!: number[];
  @Input() gameData!: GameData;
  @Input() changeFontSize!: (ref: ElementRef) => void;

  @Output() hostGameEvent = new EventEmitter<object>();
  @Output() chosenClue = new EventEmitter<any>();
  @Output() onBuzzIn = new EventEmitter<void>();
  @Output() onAnswer = new EventEmitter<string>();
  @Output() onToWaiting = new EventEmitter<string>();

  @ViewChild(BoardComponent) boardComponent!: BoardComponent;
  @ViewChild(ClueComponent) clueComponent!: ClueComponent;

  private clueSubject = new ReplaySubject<any>(1);
  clueObservable$: Observable<any> = this.clueSubject.asObservable();

  handleGameStateChange(data: any) {
    this.chosenClue.emit({ category: data.category, clue: data.clue });
  }

  startFlickerClue(
    category_idx: number,
    clue_idx: number,
    duration: number
  ): void {
    // a clue has been chosen flicker the chosen clue
    this.boardComponent.startFlickerClue(category_idx, clue_idx, duration);
  }

  startProgressBar(duration: number): void {
    // this.clueComponent.startProgressBar(duration);
    this.clueSubject.next({ action: 'startProgressBar', duration: duration });
  }

  pauseProgressBar(): void {
    this.clueComponent.pauseProgressBar();
  }

  unpause(duration: number): void {
    this.clueComponent.runProgressBar(duration, this.clueComponent.progress);
    this.clueComponent.banner = this.clueComponent.BannerType.Empty;
  }

  otherAnswering(): void {
    this.clueComponent.answeringText =
      this.players[this.gameData.answeringIndex].username + ' is answering...';
    this.clueComponent.banner = this.clueComponent.BannerType.AltAnswering;
  }

  startAnswering(duration: number): void {
    this.clueComponent.banner = this.clueComponent.BannerType.Answering;
    this.clueComponent.startAnsweringTimer(duration)
    this.clueComponent.buzzedIn = true;
  }

  startAnsweringTimer(duration: number): void {
    this.clueComponent.startAnsweringTimer(duration);
  }

  handleBuzzIn(): void {
    this.onBuzzIn.emit();
  }

  handleAnswer(ans: string): void {
    this.onAnswer.emit(ans);
  }

  handleToWaiting(): void {
    this.onToWaiting.emit();
  }

  handleLeaveGame(event: any) {
    this.hostGameEvent.emit({ state: PageStates.Landing });
  }

  handleResponse(correct: boolean, text: string): void {
    if (correct) {
      this.clueComponent.banner = this.clueComponent.BannerType.Green;
    } else {
      this.clueComponent.banner = this.clueComponent.BannerType.Red;
    }
    this.clueComponent.bannerText =
      this.players[this.gameData.answeringIndex].username +
      ': Who/What is ' +
      text +
      '?';
  }

  displayCorrectAnswer(text: string): void {
    this.clueComponent.banner = this.clueComponent.BannerType.Green;
    this.clueComponent.bannerText =
      'We were looking for' + ': Who/What is ' + text + '?';
  }
}
