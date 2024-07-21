import { Injectable } from '@angular/core';

export interface Player {
  username: string;
  score: number;
}

@Injectable({
  providedIn: 'root',
})
export class GameData {
	numCategories = 0;
	numClues = 0;

	categoryTitles: string[];
	prices: number[];

	playerCash: number[];
}