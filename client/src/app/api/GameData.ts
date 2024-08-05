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
	givenCategories: string[];
	state: string = '';

	categoryTitles: string[];
	prices: number[];

	isPicker: boolean;
	pickerIndex: number;

	current_clue: string;
	buzz_in_duration: number;

	picked: {[key: string] : { [key: string] : boolean}};
	answering = false;
	answeringIndex:number;
}