import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class GameData {
	gameState = null;

	numCategories = 0;
	numClues = 0;
}