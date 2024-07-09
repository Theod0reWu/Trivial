import { Injectable } from '@angular/core';
import { Observable, take, lastValueFrom } from 'rxjs';
import { SocketService } from './socket.service';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
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

	players : Array<Record<string, string>> = [];

	private socketService : SocketService = new SocketService();
	socketConnected = false;

	playerChange$ : Observable<any>;

	setUsername(username : string) : void {
		this.username = username;
	}

	setRoom(roomId: string): void {
		this.roomId = roomId;
	}

	setHost(isHost: boolean) : void {
		this.host = isHost;
	}

	reset() : void {
		this.roomId = '';
        this.host = false;
        this.sessionId = '';
        this.socketConnected = false;
        this.players = [];
	}

	isValidRoom(roomId : string): Observable<any> {;
		return this.apiService.validRoom(roomId);
	}

	connectToRoom(): boolean{
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
		this.apiService.createSession(this.roomId).subscribe( {
	    next: (result) => {
	      this.sessionId = result["session_id"];
	    },
	    error: (err) => {
	      console.error("Observable for creating a session emitted error:" + err);
	      this.socketConnected = false;
	    }, 
	    complete: () => {
	      //setup socket with sessionId and roomId
	      this.socketService.initSocket(this.sessionId);
	      this.socketService.joinRoom(this.roomId, this.username, this.sessionId);
	      this.socketConnected = true;

	      // setup for when players join a room
	      this.playerChange$ = this.socketService.onPlayerChange();
	      this.playerChange$.subscribe( {
	      	next: (result) => {
	      		this.players = [];
	      		for (var player of result) {
	      			this.players.push({"username" : player});
	      		}
	      		this.apiService.isHost(this.sessionId).subscribe( {
	      			next: (value) => {
	      				this.host = value["is_host"];
	      				console.log(this.sessionId, this.host);
	      			}
	      		});
	      	}
	      });
	    }
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
