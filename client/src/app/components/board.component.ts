import {
  AfterViewInit,
  Component,
  EventEmitter,
  Input,
  Output,
} from '@angular/core';
// import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { NgClass, NgForOf } from '@angular/common';

@Component({
  selector: 'board-view',
  standalone: true,
  imports: [NgForOf, NgClass],
  templateUrl: '../components_html/board.component.html',
  styleUrl: '../components_css/board.component.css',
})
export class BoardComponent implements AfterViewInit {
  //   @Output() hostGameEvent = new EventEmitter<PageStates>();

  /* 
  API get on init - who is currently choosing, board state, scores, players
  On choice - which clue was chosen
  */

  isChoosing = true; // temp var for player currently choosing
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

  categories = [
    'Category 1',
    'Category 2',
    'Category 3',
    'Category 4',
    'Category 5',
    'Category 6',
  ];
  numRows = 5;
  numCols = 6;
  startingPrice = 200;
  priceIncrement = 200;

  generatePricesArray(count: number): Array<number> {
    let prices = [];
    for (let i = 0; i < count; ++i) {
      prices.push(
        this.startingPrice + this.priceIncrement * Math.floor(i / this.numCols)
      );
    }
    return prices;
  }

  ngAfterViewInit() {
    this.initScrollSync();
  }

  initScrollSync() {
    const mainContainer = document.querySelector('.main') as HTMLElement;
    const boardContainer = document.querySelector('.board') as HTMLElement;
    const playerFogContainer = document.querySelector(
      '.player-fog'
    ) as HTMLElement;
    mainContainer.addEventListener('scroll', () => {
      boardContainer.scrollTop = mainContainer.scrollTop;
      playerFogContainer.scrollTop = mainContainer.scrollTop;
    });
    boardContainer.addEventListener('wheel', (event) => {
      mainContainer.scrollTop += event.deltaY;
    });
    playerFogContainer.addEventListener('wheel', (event) => {
      mainContainer.scrollTop += event.deltaY;
    });
  }
}
