import { Injectable } from '@angular/core';

export interface Player {
  username: string;
  score: number;
}

@Injectable({
  providedIn: 'root',
})
export class GameData {
	numCategories: number = 0;
	numClues: number = 0;
	state: string = '';

	categoryTitles: string[];
	prices: number[];

	playerCash: number[];
	isPicker: boolean;

	current_clue: string;
}