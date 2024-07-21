import {
  AfterViewInit,
  Component,
  EventEmitter,
  Input,
  Output,
} from '@angular/core';
// import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { NgClass, NgForOf, CommonModule } from '@angular/common';
import { Player } from '../api/GameData';

@Component({
  selector: 'board-view',
  standalone: true,
  imports: [NgForOf, NgClass, CommonModule],
  templateUrl: '../components_html/board.component.html',
  styleUrl: '../components_css/board.component.css',
})
export class BoardComponent implements AfterViewInit {
  //   @Output() hostGameEvent = new EventEmitter<PageStates>();
  @Input() players!: Player[];
  @Input() scores!: number[];
  @Input() numRows!: number;
  @Input() numCols!: number;
  @Input() categories!: string[];
  @Input() prices!: number[];
  @Output() gameStateChange = new EventEmitter<boolean>();
  /* 
  API get on init - who is currently choosing, board state, scores, players
  On choice - which clue was chosen
  */
  ngOnInit(): void {
    
  }

  isChoosing = true; // temp var for player currently choosing

  // numRows = 5;
  // numCols = 6;
  startingPrice = 200;
  priceIncrement = 200;

  range(to: number): number[] {
    let x = [];
    for (let i = 0; i < to; ++i) {
      x.push(i);
    }
    return x;
  }

  getGridTemplateCategories(): string {
    return `repeat(${this.numCols}, 1fr)`;
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
