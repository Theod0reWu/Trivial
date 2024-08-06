import {
  AfterViewInit,
  Component,
  ElementRef,
  HostListener,
  Input,
  QueryList,
  ViewChildren,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Player } from '../api/GameData';

@Component({
  selector: 'players-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: '../components_html/players_list.component.html',
})
export class PlayersListComponent implements AfterViewInit {
  @Input() players!: Player[];
  @Input() displayState!: string;
  @Input() pickerIndex!: number;
  @Input() changeFontSize!: (ref: ElementRef) => void;

  @ViewChildren('username') usernames!: QueryList<ElementRef>;
  @ViewChildren('score') scores!: QueryList<ElementRef>;
  @HostListener('window:resize', ['$event']) onResize(event: any) {
    this.usernames.toArray().forEach((child) => {
      this.changeFontSize(child);
    });
    this.scores.toArray().forEach((child) => {
      this.changeFontSize(child);
    });
  }

  ngAfterViewInit() {
    const changeFontSizes = () => {
      this.usernames.toArray().forEach((child) => {
        this.changeFontSize(child);
      });
      this.scores.toArray().forEach((child) => {
        this.changeFontSize(child);
      });
    };
    this.usernames.changes.subscribe(changeFontSizes);
    this.scores.changes.subscribe(changeFontSizes);
    changeFontSizes();
  }
}
