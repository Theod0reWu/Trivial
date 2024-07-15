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
import { Player } from './game.component';

@Component({
  selector: 'board-view',
  standalone: true,
  imports: [NgForOf, NgClass],
  templateUrl: '../components_html/board.component.html',
  styleUrl: '../components_css/board.component.css',
})
export class BoardComponent implements AfterViewInit {
  //   @Output() hostGameEvent = new EventEmitter<PageStates>();
  @Input() players!: Player[];
  @Output() gameStateChange = new EventEmitter<boolean>();
  /* 
  API get on init - who is currently choosing, board state, scores, players
  On choice - which clue was chosen
  */

  isChoosing = true; // temp var for player currently choosing

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
    // this.initScrollSync();
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

  onClickClue(event: MouseEvent) {
    // TODO: confirm that it is the player's turn for who clicked first
    const target = event.target as HTMLElement;
    const clueBackground = document.querySelector('.clue-bg') as HTMLElement;

    let isBorderVisible = false;
    const flickerInterval = 200;
    const flickerDuration = 2000;

    const intervalId = setInterval(() => {
      if (isBorderVisible) {
        target.style.outline = 'none';
      } else {
        target.style.outline = '5px solid white';
      }
      isBorderVisible = !isBorderVisible;
    }, flickerInterval);

    setTimeout(() => {
      clearInterval(intervalId);
      target.style.outline = 'none';
      clueBackground.style.width = '100vw';
      clueBackground.style.height = '100vh';
    }, flickerDuration);

    setTimeout(() => {
      this.gameStateChange.emit(false);
      clueBackground.style.width = '0';
      clueBackground.style.height = '0';
    }, flickerDuration + 1000);
  }
}
