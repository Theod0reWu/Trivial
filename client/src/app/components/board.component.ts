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
import { Player, GameData } from '../api/GameData';

const FLICKER_INTERVAL = 200;

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
  @Input() gameData: GameData;
  @Output() gameStateChange = new EventEmitter<any>();
  /* 
  API get on init - who is currently choosing, board state, scores, players
  On choice - which clue was chosen
  */
  ngOnInit(): void {}

  isChoosing = true; // temp var for player currently choosing
  intervalId: any = null;
  chosenClue: HTMLElement;

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
    for (let i = 0; i < this.numCols; ++i) {
      for (let e = 0; e < this.numRows; ++e) {
        if (this.gameData.picked[String(i)][String(e)]) {
          let clue = document.getElementById(
            (i + e * this.numCols).toString()
          ) as HTMLElement;
          clue.style.color = 'var(--gold-transparent-20)';
          clue.setAttribute('pointer-events', 'none');
        }
      }
    }
  }

  getCategoryIndex(index: number) {
    console.log(index);
    return String(index % this.numCols);
  }

  getClueIndex(index: number) {
    return String(Math.floor(index / this.numCols));
  }

  onClickClue(event: MouseEvent): void {
    if (!this.gameData.isPicker || this.intervalId) {
      return;
    }
    // get and send the chosen clue to the server
    this.chosenClue = event.target as HTMLElement;

    let index = Number(this.chosenClue.id);
    let category_idx = index % this.numCols;
    let clue_idx = Math.floor(index / this.numCols);
    this.gameStateChange.emit({ category: category_idx, clue: clue_idx });
  }

  startFlickerClue(
    category_idx: number,
    clue_idx: number,
    duration: number
  ): void {
    let total_idx = category_idx + clue_idx * this.numCols;
    this.chosenClue = document.getElementById(
      total_idx.toString()
    ) as HTMLElement;
    this.startFlicker();

    let realDuration = duration * 1000;
    const clueBackground = document.querySelector('.clue-bg') as HTMLElement;
    setTimeout(() => {
      clearInterval(this.intervalId);
      // this.intervalId = null;

      this.chosenClue.style.outline = 'none';
      clueBackground.style.width = '100vw';
      clueBackground.style.height = '100vh';
    }, realDuration / 2);

    setTimeout(() => {
      this.intervalId = null;
      clueBackground.style.width = '0';
      clueBackground.style.height = '0';
    }, realDuration + 1500);
  }

  startFlicker(): void {
    /*
      Expects this.clueChosen to be set to the HTMLElement of the selected clue

      sets this.intervalId
    */
    let isBorderVisible = false;
    this.intervalId = setInterval(() => {
      if (isBorderVisible) {
        this.chosenClue.style.outline = 'none';
      } else {
        this.chosenClue.style.outline = '5px solid white';
      }
      isBorderVisible = !isBorderVisible;
    }, FLICKER_INTERVAL);
  }
}
