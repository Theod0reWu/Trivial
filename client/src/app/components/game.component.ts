import { Component, Input } from '@angular/core';
// import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { BoardComponent } from './board.component';
import { ClueComponent } from './clue.component';
import { Player } from '../api/GameData';

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

  boardView = true;

  handleGameStateChange(boardView: boolean) {
    this.boardView = boardView;
  }
}
