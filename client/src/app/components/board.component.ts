import { Component, EventEmitter, Input, Output } from '@angular/core';
// import { NgOptimizedImage } from '@angular/common';
import { PageStates } from '../app.component';
import { NgForOf } from '@angular/common';

@Component({
  selector: 'board-view',
  standalone: true,
  imports: [NgForOf],
  templateUrl: '../components_html/board.component.html',
  styleUrl: '../components_css/board.component.css',
})
export class BoardComponent {
  //   @Output() hostGameEvent = new EventEmitter<PageStates>();

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
  //   clickedJoinGame = false;
  //   onClickJoinGame() {
  //     this.clickedJoinGame = true;
  //   }
  //   onClickHostGame() {
  //     this.hostGameEvent.emit(PageStates.Waiting);
  //   }
}
