import { Injectable } from '@angular/core';
import { Observable, take, lastValueFrom, Subject } from 'rxjs';
import { SocketService } from './socket.service';
import { ApiService } from './api.service';
import { GameData, Player } from './GameData';

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
  reconnecting: boolean = false;

  players: Player[] = [];

  private socketService: SocketService = new SocketService();
  socketConnected = false;

  gameStateChange$: Observable<any>;
  gameData: GameData = new GameData();

  // observables for picking up socket responses
  hostChange$: Observable<any>;
  playerChange$: Observable<any>;
  pickingChange$: Observable<any>;
  clueChange$: Observable<any>;
  pausedChange$: Observable<any>;
  answeringChange$: Observable<any>;
  responseChange$: Observable<any>;
  waitingChange$: Observable<any>;

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

  startGame(
    numCategories: number,
    numClues: number,
    givenCategories: string[]
  ): void {
    this.socketService.startGame(
      this.roomId,
      this.sessionId,
      numCategories,
      numClues,
      givenCategories
    );
    this.loading = true;
  }

  sendBoardChoice(category: number, clue: number): void {
    this.socketService.sendBoardChoice(
      this.roomId,
      this.sessionId,
      category,
      clue
    );
  }

  sendBuzzIn(): void {
    this.socketService.sendBuzzIn(this.roomId, this.sessionId);
  }

  sendAnswer(answer: string): void {
    this.socketService.sendAnswer(this.roomId, this.sessionId, answer);
  }

  sendToWaiting(): void {
    this.socketService.sendToWaiting(this.roomId, this.sessionId);
  }

  setupSocketEvents(): void {
    /*
      Sets up subscriptions for when socket receives data that needs to update member vars.

      modifies asynchronously:
        this.sockerService
        this.players
        this.host
        this.gameData
    */

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

    this.socketService.onPlayerCash().subscribe({
      next: (value) => {
        for (let c = 0; c < value.length; ++c) {
          this.players[c].score = value[c];
        }
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
      },
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
        this.gameData.numClues = value['num_clues'];
        this.gameData.numCategories = value['num_categories'];
        this.gameData.categoryTitles = value['category_titles'];
        this.gameData.prices = [];
        for (let i = 0; i < this.gameData.numClues; ++i) {
          for (let e = 0; e < this.gameData.numCategories; ++e) {
            this.gameData.prices.push(value['prices'][i]);
          }
        }
      },
    });

    this.pickingChange$ = this.socketService.onPicking();
    this.clueChange$ = this.socketService.onClue();
    this.pausedChange$ = this.socketService.onPaused();
    this.answeringChange$ = this.socketService.onAnswering();
    this.responseChange$ = this.socketService.onResponse();
    this.waitingChange$ = this.socketService.onSwitchWaiting();

    this.socketService.onPickerIndex().subscribe({
      next: (value) => {
        this.gameData.pickerIndex = value;
      },
    });

    this.socketService.onPicked().subscribe({
      next: (value) => {
        this.gameData.picked = value;
      },
    });
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
    if (this.roomId === '' || this.username === '' || this.socketConnected) {
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
        if (this.reconnecting) {
          this.reconnectSocket();
        }
      },
    });
    return true;
  }

  disconnectFromRoom(): void {
    /*
			disconnects from this.roomId and clears all the associated data (roomId and sessionId)
		*/
    if (this.roomId == '' || this.roomId == null) {
      return;
    }
    this.socketService.leaveRoom(this.roomId, this.sessionId);
    this.socketService.disconnectSocket();
    this.reset();
  }

  reconnect(reconnector: Subject<any>): void {
    /*
      Check if reconnecting possible

      Modifies asynchronously:
        this.reconnecting
      possible updates:
        this.sessionId
        this.roomId
        this.host
        this.username
    */
    this.apiService.getSession().subscribe({
      next: (result) => {
        this.reconnecting = result['reconnect'];
        if (this.reconnecting){
          this.sessionId = result['session_id'];
          this.roomId = result['room_id'];
          this.host = false;
          this.username = result['username'];
        }
      },
      error: (err) => {},
      complete: () => {
        if (this.reconnecting) {
          this.socketService.initSocket(this.sessionId);
        }
        reconnector.next({ reconnect: this.reconnecting });
      },
    });
  }

  reconnectSocket(): void {
    this.socketService.reconnect(this.roomId, this.sessionId);
  }
}
