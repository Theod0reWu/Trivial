import { Injectable } from '@angular/core';

export interface Player {
  username: string;
  score: number;
}

@Injectable({
  providedIn: 'root',
})
export class GameData {
	/* 
		Stores relevant game data

		The data is provided by the server
	*/

	// Initial game data (can also be set as the host)
	numCategories: number = 0;
	numClues: number = 0;
	givenCategories: string[];

	// game state (board, clue, answering, done)
	state: string = '';

	// board data
	categoryTitles: string[];
	prices: number[];

	// who is picking and which clues have been picked
	isPicker: boolean;
	pickerIndex: number;
	picked: {[key: string] : { [key: string] : boolean}};

	// data for the current clue and timer duration
	current_clue: string;
	buzz_in_duration: number;

	// who is answering
	answering = false;
	answeringIndex:number;
}