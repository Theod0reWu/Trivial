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

  @ViewChild(BoardComponent) boardComponent!: BoardComponent; 
  @ViewChild(ClueComponent) clueComponent!: ClueComponent;

  handleGameStateChange(data: any) {
    this.chosenClue.emit({category: data.category, clue: data.clue});
  }

  startFlickerClue(category_idx: number, clue_idx: number, duration: number): void {
    this.boardComponent.startFlickerClue(category_idx, clue_idx, duration);
  }

  startProgressBar(duration: number): void {
    this.clueComponent.startProgressBar(duration);
  }
}
