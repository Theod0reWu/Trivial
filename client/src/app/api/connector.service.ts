import { Injectable } from '@angular/core';
import { Observable, take, lastValueFrom } from 'rxjs';
import { SocketService } from './socket.service';
import { ApiService } from './api.service';
import { GameData, Player} from './GameData';

@Injectable({
  providedIn: 'root',
})
export class ConnectorService {
  /*
		Handles all connections to the backend. This includes REST api requests and socket connections.
	*/
  constructor(private apiService: ApiService) {}

  roomId: string = '';
  host: boolean = false; // should be true for the host and false for everyone else
  sessionId: string = '';
  username: string = '';

  hostChange$: Observable<any>;
  playerChange$: Observable<any>;
  players: Player[] = [];

  private socketService: SocketService = new SocketService();
  socketConnected = false;

  gameStateChange$: Observable<any>;
  gameData: GameData = new GameData();

  pickingChange$: Observable<any>;
  clueChange$: Observable<any>;
  pausedChange$: Observable<any>;
  answeringChange$: Observable<any>;

  loading = false;

  setUsername(username: string): void {
    this.username = username;
  }

  setRoom(roomId: string): void {
    this.roomId = roomId;
  }

  setHost(isHost: boolean): void {
    this.host = isHost;
  }

  reset(): void {
    this.roomId = '';
    this.host = false;
    this.sessionId = '';
    this.socketConnected = false;
    this.players = [];
    this.loading = false;
  }

  isValidRoom(roomId: string): Observable<any> {
    return this.apiService.validRoom(roomId);
  }

  startGame(numCategories: number, numClues: number): void {
    this.socketService.startGame(
      this.roomId,
      this.sessionId,
      numCategories,
      numClues
    );
    this.loading = true;
  }

  sendBoardChoice(category: number, clue: number): void {
  	this.socketService.sendBoardChoice(this.roomId, this.sessionId, category, clue);
  }

  sendBuzzIn(): void {
  	this.socketService.sendBuzzIn(this.roomId, this.sessionId);
  }

  setupSocketEvents(): void {
  	// setup for when players join a room
    this.playerChange$ = this.socketService.onPlayerChange();
    this.playerChange$.subscribe({
      next: (result) => {
        this.players = [];
        for (var player of result) {
          this.players.push({ username: player, score: 0 });
        }

        //old method for determining host
        // this.apiService.isHost(this.sessionId).subscribe({
        //   next: (value) => {
        //     this.host = value['is_host'];
        //   },
        // });
      },
    });

    // setup for when a new host needs to be elected after original leaves
    this.hostChange$ = this.socketService.onHost();
    this.hostChange$.subscribe({
      next: (value) => {
        this.host = true;
      },
    });

    this.socketService.onPicker().subscribe({
    	next: (value) => {
    		this.gameData.isPicker = value;
    		console.log("I am picking:", this.gameData.isPicker);
    	}
    });

    // setup for game state is being emitted
    this.gameStateChange$ = this.socketService.onGameState();
    this.gameStateChange$.subscribe({
      next: (value) => {
        this.gameData.state = value;
      },
    });

    // setup for when board data is being transmitted (category titles and cost of clues)
    this.socketService.onBoardData().subscribe({
    	next: (value) => {
    		this.gameData.numClues = value["num_clues"];
    		this.gameData.numCategories = value["num_categories"];
    		this.gameData.categoryTitles = value["category_titles"];
    		this.gameData.prices = [];
    		for (let i = 0; i < this.gameData.numClues; ++i){
    			for (let e = 0; e < this.gameData.numCategories; ++e) {
    				this.gameData.prices.push(value["prices"][i]);
    			}
    		}
    	}
    });

    this.pickingChange$ = this.socketService.onPicking();
    this.clueChange$ = this.socketService.onClue();
    this.pausedChange$ = this.socketService.onPaused();
    this.answeringChange$ = this.socketService.onAnswering();

    this.socketService.onPickerIndex().subscribe({
    	next: (value) => {
    		this.gameData.pickerIndex = value;
    		console.log("picker:", value);
    	}
    })
  }

  connectToRoom(callback: Function): boolean {
    /*
			Ensure this.setRoom(...) and this.setUsername(...) is called first.
			Connects to the room specified in this.roomId by creating the sessionId and setting up a socket.
			Returns true for sucessfully connecting to the room. 

			Acesses:
				this.username
				this.roomId

			Modifies:
				this.sessionId
		*/
    if (this.roomId == '' || this.username == '' || this.socketConnected) {
      return false;
    }
    this.apiService.createSession(this.roomId, this.username).subscribe({
      next: (result) => {
        this.sessionId = result['session_id'];
      },
      error: (err) => {
        console.error('Observable for creating a session emitted error:' + err);
        this.socketConnected = false;
      },
      complete: () => {
        //setup socket with sessionId and roomId
        this.socketService.initSocket(this.sessionId);
        this.socketService.joinRoom(this.roomId, this.username, this.sessionId);
        this.socketConnected = true;
        this.setupSocketEvents();

        callback();
      },
    });
    return true;
  }

  disconnectFromRoom(): void {
    /*
			disconnects from this.roomId and clears all the associated data (roomId and sessionId)
		*/
    if (this.roomId == '') {
      return;
    }
    this.socketService.leaveRoom(this.roomId, this.sessionId);
    this.socketService.disconnectSocket();
    this.reset();
  }
}
