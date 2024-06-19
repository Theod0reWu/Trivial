import { Component } from '@angular/core';
// import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { BoardComponent } from './board.component';
import { ClueComponent } from './clue.component';

export interface Player {
  username: string;
  score: number;
}

@Component({
  selector: 'game-view',
  standalone: true,
  imports: [BoardComponent, ClueComponent],
  templateUrl: '../components_html/game.component.html',
})
export class GameComponent {
  boardView = true;
  players = [
    // temp players list
    { username: 'Winxler', score: 0 },
    { username: 'niflac', score: 0 },
    { username: 'Teoz', score: 0 },
    { username: 'Dylan', score: 0 },
    { username: 'Winxler', score: 0 },
    { username: 'niflac', score: 0 },
    { username: 'Teoz', score: 0 },
    { username: 'Dylan', score: 0 },
    { username: 'Winxler', score: 0 },
    { username: 'niflac', score: 0 },
    { username: 'Teoz', score: 0 },
    { username: 'Dylan', score: 0 },
  ];

  handleGameStateChange(boardView: boolean) {
    this.boardView = boardView;
  }
}
