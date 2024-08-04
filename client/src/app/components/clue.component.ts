import {
  Component,
  ElementRef,
  EventEmitter,
  HostListener,
  Input,
  Output,
  ViewChild,
} from '@angular/core';
import { PageStates } from '../app.component';
import { NgClass, NgForOf, CommonModule, NgIf } from '@angular/common';
import { Player } from '../api/GameData';
import { TimerComponent } from './timer.component';
import { ReactiveFormsModule } from '@angular/forms';
import { FormGroup, FormControl } from '@angular/forms';
import { Observable, Subject, BehaviorSubject, ReplaySubject } from 'rxjs';
import { PlayersListComponent } from './player_list.component';

enum BannerStates {
  Empty = 'empty',
  Green = 'green',
  Red = 'red',
  AltAnswering = 'altanswering',
  Answering = 'answering',
}

@Component({
  selector: 'clue-view',
  standalone: true,
  imports: [
    NgForOf,
    NgIf,
    NgClass,
    CommonModule,
    TimerComponent,
    ReactiveFormsModule,
    PlayersListComponent,
  ],
  templateUrl: '../components_html/clue.component.html',
  styleUrl: '../components_css/clue.component.css',
})
export class ClueComponent {
  public _clue!: string;

  @Input() players!: Player[];
  @Input() scores!: number[];
  @Input() set clue(value: string) {
    this._clue = value;
    // dynamically set font size
    this.changeFontSize();
  }
  @Input() onMessage$: Observable<any>;

  @Output() gameStateChange = new EventEmitter<boolean>();
  @Output() onBuzzIn: EventEmitter<void> = new EventEmitter<void>();
  @Output() onAnswer: EventEmitter<string> = new EventEmitter<string>();

  @ViewChild('clueText') clueText!: ElementRef;
  @HostListener('window:resize', ['$event']) onResize(event: any) {
    this.changeFontSize();
  }

  constructor() {
    this.form = new FormGroup({
      answer: new FormControl(''),
    });
  }

  form: FormGroup;

  // variables for progress bar
  progress: number = 0;
  start_time: number;
  progress_interval: any;
  timeout: any;

  public buzzedIn: boolean = false;

  // to control the timer
  private timerSubject = new ReplaySubject<any>(1);
  public timerObservable$ = this.timerSubject.asObservable();

  ngAfterViewInit(): void {
    this.onMessage$.subscribe({
      next: (value) => {
        if (value['action'] === 'startProgressBar') {
          this.startProgressBar(value['duration']);
        }
      },
    });
    this.changeFontSize();
  }

  sendBuzzIn(): void {
    if (!this.buzzedIn) {
      this.onBuzzIn.emit();
      this.buzzedIn = true;
    }
  }

  pauseProgressBar(): void {
    clearInterval(this.progress_interval);
    clearTimeout(this.timeout);
  }

  startProgressBar(duration: number): void {
    this.buzzedIn = false;
    this.runProgressBar(duration, 0);
  }

  runProgressBar(duration: number, initial_progress: number): void {
    this.start_time = new Date().getTime();
    this.progress_interval = setInterval(() => {
      let time = new Date().getTime();
      this.progress =
        ((time - this.start_time) / (1000 * duration)) *
          (1 - initial_progress) +
        initial_progress;
    }, 16);

    this.timeout = setTimeout(() => {
      clearInterval(this.progress_interval);
    }, duration * 1000);
  }

  startAnsweringTimer(duration: number): void {
    // this.timerComponent.start(duration);
    this.timerSubject.next({ action: 'start', duration: duration });
  }

  onSubmitAnswer() {
    // console.log('Form Data: ', this.form.value);
    this.onAnswer.emit(this.form.value['answer']);
  }

  isOverflown(element: any) {
    return (
      element &&
      (element.scrollHeight > element.clientHeight ||
        element.scrollWidth > element.clientWidth)
    );
  }

  changeFontSize() {
    if (!this.clueText) return;
    let fontSize = parseInt(
      getComputedStyle(this.clueText.nativeElement).getPropertyValue(
        'font-size'
      )
    );
    let overflow = this.isOverflown(this.clueText.nativeElement);

    if (overflow) {
      // shrink text
      for (let i = fontSize; i > 1; --i) {
        if (overflow) {
          --fontSize;
          this.clueText.nativeElement.style.fontSize = fontSize + 'px';
        }
        overflow = this.isOverflown(this.clueText.nativeElement);
      }
    } else {
      // grow text
      while (!overflow) {
        ++fontSize;
        this.clueText.nativeElement.style.fontSize = fontSize + 'px';
        overflow = this.isOverflown(this.clueText.nativeElement);
      }
      --fontSize;
      this.clueText.nativeElement.style.fontSize = fontSize + 'px';
    }
  }

  BannerType = BannerStates;
  banner = BannerStates.Empty;

  bannerText = 'Who/What is Berlin?';
  answeringText = 'Team 1 is answering';

  timerFraction = 0.5;
}
