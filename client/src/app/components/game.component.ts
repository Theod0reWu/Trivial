import { 
  Component, 
  Input, 
  Output, 
  EventEmitter, 
  ViewChild, 
} from '@angular/core';
// import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { BoardComponent } from './board.component';
import { ClueComponent } from './clue.component';
import { Player, GameData} from '../api/GameData';

@Component({
  selector: 'game-view',
  standalone: true,
  imports: [BoardComponent, ClueComponent],
  templateUrl: '../components_html/game.component.html',
})
export class GameComponent {
  @Input() numCols!: number;
  @Input() numRows!: number;
  @Input() categoryTitles!: string[];
  @Input() players!: Player[];
  @Input() prices!: number[];
  @Input() gameData!: GameData;

  @Output() chosenClue = new EventEmitter<any>();
  @Output() onBuzzIn = new EventEmitter<void>();

  @ViewChild(BoardComponent) boardComponent!: BoardComponent; 
  @ViewChild(ClueComponent) clueComponent!: ClueComponent;

  handleGameStateChange(data: any) {
    this.chosenClue.emit({category: data.category, clue: data.clue});
  }

  startFlickerClue(category_idx: number, clue_idx: number, duration: number): void {
    // a clue has been chosen flicker the chosen clue
    this.boardComponent.startFlickerClue(category_idx, clue_idx, duration);
  }

  startProgressBar(duration: number): void {
    this.clueComponent.startProgressBar(duration);
    this.clueComponent.buzzedIn = false;
  }

  pauseProgressBar(): void {
    this.clueComponent.pauseProgressBar();
  }

  resumeProgressBar(duration:number): void {
    this.clueComponent.runProgressBar(duration, this.clueComponent.progress);
  }

  startAnswering(duration: number): void {
    this.clueComponent.banner = this.clueComponent.BannerType.Answering;
  }

  handleBuzzIn(): void {
    this.onBuzzIn.emit();
  }
}
