import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  Output,
  Renderer2,
  ViewChild,
} from '@angular/core';
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

  sortedPlayers: Player[] = [];
  podium: Player[] = [];
  nonPodium: Player[] = [];

  @Output() leaveGame = new EventEmitter<object>();
  @Output() toWaiting = new EventEmitter<object>();
  @Output() gameStateChange = new EventEmitter<any>();

  @ViewChild('main') mainElement!: ElementRef;
  constructor(private renderer2: Renderer2) {}

  ngOnInit() {
    this.updatePlayers();
  }

  ngAfterViewInit() {
    this.celebrate();
    let bgAudio = document.getElementById('bgAudio') as HTMLAudioElement;
    bgAudio.volume = 0.2;
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
    const canvas = this.renderer2.createElement('canvas');

    this.renderer2.appendChild(this.mainElement.nativeElement, canvas);

    const myConfetti = confetti.create(canvas, {
      resize: true, // will fit all screen sizes
      // disableForReducedMotion: true,
    });

    const duration = 15 * 1000;
    var animationEnd = Date.now() + duration;
    const fireworksDefaults = {
      startVelocity: 30,
      spread: 360,
      ticks: 60,
      zIndex: 0,
    };
    const starsDefaults = {
      spread: 360,
      ticks: 50,
      gravity: 0,
      decay: 0.94,
      startVelocity: 30,
      colors: ['FFE400', 'FFBD00', 'E89400', 'FFCA6C', 'FDFFB8'],
      origin: { y: 0.3 },
    };

    var randomInRange = (min: number, max: number) => {
      return Math.random() * (max - min) + min;
    };

    var interval: any = setInterval(function () {
      var timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      var particleCount = 75 * (timeLeft / duration);
      // since particles fall down, start a bit higher than random
      myConfetti({
        ...fireworksDefaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
      });
      myConfetti({
        ...fireworksDefaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
      });
    }, 250);

    var shootStars = () => {
      myConfetti({
        ...starsDefaults,
        particleCount: 50,
        scalar: 1.2,
        shapes: ['star'],
      });

      myConfetti({
        ...starsDefaults,
        particleCount: 10,
        scalar: 0.75,
        shapes: ['circle'],
      });
    };
    for (var i = 400; i <= 800; i += 100) {
      setTimeout(shootStars, i);
    }
  }
}
