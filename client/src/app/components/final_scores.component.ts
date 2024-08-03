import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
} from '@angular/core';
import { PageStates } from '../app.component';
import { NgClass, NgForOf, CommonModule } from '@angular/common';
import { Player } from '../api/GameData';

@Component({
  selector: 'final-scores-view',
  standalone: true,
  imports: [NgForOf, NgClass, CommonModule],
  templateUrl: '../components_html/final_scores.component.html',
  styleUrl: '../components_css/final_scores.component.css',
})
export class FinalScoresComponent implements OnChanges {
  @Input() players!: Player[];
  @Input() isHost!: boolean;
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
  @Output() gameStateChange = new EventEmitter<any>();

  ngOnInit() {
    this.updatePlayers();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['players']) {
      this.updatePlayers();
    }
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
}
