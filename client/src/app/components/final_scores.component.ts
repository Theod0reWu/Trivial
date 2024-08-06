import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  Renderer2,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { PageStates } from '../app.component';
import { NgClass, NgForOf, CommonModule } from '@angular/common';
import { Player } from '../api/GameData';
import * as confetti from 'canvas-confetti';

@Component({
  selector: 'final-scores-view',
  standalone: true,
  imports: [NgForOf, NgClass, CommonModule],
  templateUrl: '../components_html/final_scores.component.html',
  styleUrl: '../components_css/final_scores.component.css',
})
export class FinalScoresComponent implements AfterViewInit {
  @Input() players!: Player[];
  @Input() isHost!: boolean;
  @Input() gameState!: string;
  // players = [
  //   { username: 'winxler', score: 1000 },
  //   { username: 'winxler2', score: 900 },
  //   { username: 'winxler3', score: 800 },
  //   { username: 'winxler4', score: 700 },
  //   { username: 'winxler5', score: 600 },
  //   { username: 'winxler6', score: 500 },
  //   { username: 'winxler6', score: 500 },
  //   { username: 'winxler6', score: 500 },
  //   { username: 'winxler6', score: 500 },
  //   { username: 'winxler6', score: 500 },
  //   { username: 'winxler6', score: 500 },
  //   { username: 'winxler6', score: 500 },
  //   { username: 'winxler6', score: 500 },
  //   { username: 'winxler6', score: 500 },
  //   { username: 'winxler7', score: 400 },
  //   { username: 'winxler8', score: 11000 },
  // ];
  sortedPlayers: Player[] = [];
  podium: Player[] = [];
  nonPodium: Player[] = [];

  @Output() leaveGame = new EventEmitter<object>();
  @Output() toWaiting = new EventEmitter<object>();
  @Output() gameStateChange = new EventEmitter<any>();

  @ViewChild('main') mainElement!: ElementRef;
  constructor(private renderer2: Renderer2, private elementRef: ElementRef) {}

  ngOnInit() {
    this.updatePlayers();
  }

  ngAfterViewInit() {
    this.celebrate();
  }

  updatePlayers() {
    this.sortedPlayers = [...this.players].sort((a, b) => b.score - a.score);
    this.podium = this.sortedPlayers.slice(0, 3);
    this.nonPodium = this.sortedPlayers.slice(3);
  }

  trackByIndex(index: number, player: { username: string; score: number }) {
    return index;
  }

  onClickLeaveGame() {
    this.leaveGame.emit();
  }

  onClickToWaiting() {
    this.toWaiting.emit();
  }

  celebrate() {
    // const duration = 5000;

    const canvas = this.renderer2.createElement('canvas');

    this.renderer2.appendChild(this.mainElement.nativeElement, canvas);

    const myConfetti = confetti.create(canvas, {
      resize: true, // will fit all screen sizes
    });

    // myConfetti({
    //   particleCount: 150,
    //   spread: 180,
    //   origin: { y: 0.6 },
    //   colors: ['#FF4500', '#008080', '#FFD700'],
    // });

    // setTimeout(() => myConfetti.reset(), duration);

    var duration = 15 * 1000;
    var animationEnd = Date.now() + duration;
    var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    function randomInRange(min: number, max: number) {
      return Math.random() * (max - min) + min;
    }

    var interval: any = setInterval(function () {
      var timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      var particleCount = 50 * (timeLeft / duration);
      // since particles fall down, start a bit higher than random
      myConfetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
      });
      myConfetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
      });
    }, 250);
  }
}
