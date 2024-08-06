import { Component, EventEmitter, Output } from '@angular/core';
import { PageStates } from '../app.component';
import { NgOptimizedImage } from '@angular/common';

@Component({
  selector: 'about-view',
  standalone: true,
  imports: [NgOptimizedImage],
  templateUrl: '../components_html/about.component.html',
  styleUrl: '../components_css/about.component.css',
})
export class AboutComponent {
  @Output() hostGameEvent = new EventEmitter<object>();

  tutorialBoardURL = '/assets/img/tutorial_board.png';
  tutorialClueURL = '/assets/img/tutorial_clue.png';

  onClickBack() {
    this.hostGameEvent.emit({ state: PageStates.Landing });
  }
}
