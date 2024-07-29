import { 
  Component, 
  EventEmitter, 
  Input, 
  Output,
  ViewChild 
} from '@angular/core';
import { PageStates } from '../app.component';
import { NgClass, NgForOf, CommonModule } from '@angular/common';
import { Player } from '../api/GameData';
import { TimerComponent } from './timer.component';
import { ReactiveFormsModule } from '@angular/forms';
import { FormGroup, FormControl } from '@angular/forms';
import { Observable, Subject, BehaviorSubject, ReplaySubject } from 'rxjs';

enum BannerStates {
  Empty = "empty",
  Green = "green",
  Red = "red",
  AltAnswering = "altanswering",
  Answering = "answering"
}

@Component({
  selector: 'clue-view',
  standalone: true,
  imports: [NgForOf, NgClass, CommonModule, TimerComponent, ReactiveFormsModule],
  templateUrl: '../components_html/clue.component.html',
  styleUrl: '../components_css/clue.component.css',
})
export class ClueComponent {
  @Input() players!: Player[];
  @Input() scores!: number[];
  @Input() clue!: string;
  @Input() onMessage$: Observable<any>;

  @Output() gameStateChange = new EventEmitter<boolean>();
  @Output() onBuzzIn: EventEmitter<void> = new EventEmitter<void>();
  @Output() onAnswer: EventEmitter<string> = new EventEmitter<string>();

  constructor() {
    this.form = new FormGroup({
      answer: new FormControl('')
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
    console.log("clue view reloaded");
    this.onMessage$.subscribe({
      next: (value) => {
        if (value["action"] === "startProgressBar"){
          this.startProgressBar(value["duration"]);
        }
      }
    });
  }

  sendBuzzIn(): void {
    if (!this.buzzedIn){
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
      this.progress = (time - this.start_time) / (1000 * duration) * (1 - initial_progress) + initial_progress;
    }, 16);

    this.timeout = setTimeout(() => {
      clearInterval(this.progress_interval);
      this.timerSubject.next({action:"none"});
    }, duration * 1000);
  }

  startAnsweringTimer(duration: number): void {
    // this.timerComponent.start(duration);
    this.timerSubject.next({action:"start", "duration": duration});
  }

  onSubmitAnswer() {
    // console.log('Form Data: ', this.form.value);
    this.onAnswer.emit(this.form.value["answer"]);
  }
  
  BannerType = BannerStates;
  banner = BannerStates.Empty;

  bannerText = "Who/What is Berlin?";
  answeringText = "Team 1 is answering";

  timerFraction = .5;

}
