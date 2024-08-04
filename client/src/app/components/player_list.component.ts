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

  isOverflown(element: any) {
    return (
      element &&
      (element.scrollHeight > element.clientHeight ||
        element.scrollWidth > element.clientWidth)
    );
  }

  changeFontSize(ref: ElementRef) {
    let fontSize = parseInt(
      getComputedStyle(ref.nativeElement).getPropertyValue('font-size')
    );
    let overflow = this.isOverflown(ref.nativeElement);

    if (overflow) {
      // shrink text
      for (let i = fontSize; i > 1; --i) {
        if (overflow) {
          --fontSize;
          ref.nativeElement.style.fontSize = fontSize + 'px';
        }
        overflow = this.isOverflown(ref.nativeElement);
      }
    } else {
      // grow text
      while (!overflow) {
        ++fontSize;
        ref.nativeElement.style.fontSize = fontSize + 'px';
        overflow = this.isOverflown(ref.nativeElement);
      }
      --fontSize;
      ref.nativeElement.style.fontSize = fontSize + 'px';
    }
  }
}
