import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class SocketService {
  private socket: Socket;

  initSocket(sessionId: string) {
    // FastAPI server url
    this.socket = io('http://localhost:8000', {
      auth: { session_id: sessionId },
    });
    this.socket.on('connect', () => {
      console.log('Connected to server');
    });
    this.socket.on('error', (err) => {
      console.error('Error connecting to server:' + err);
    });
  }

  disconnectSocket() {
    this.socket.disconnect();
  }

  // Emit an event to join a room
  joinRoom(roomId: string, username: string, sessionId: string): void {
    this.socket.emit('join_room', {
      room_id: roomId,
      username: username,
      session_id: sessionId,
    });
  }

  // Emit an event to leave a room
  leaveRoom(roomId: string, sessionId: string): void {
    this.socket.emit('leave_room', { room_id: roomId, session_id: sessionId });
  }

  //start game
  startGame(
    roomId: string,
    sessionId: string,
    numCategories: number,
    numClues: number
  ): void {
    this.socket.emit('start_game', {
      room_id: roomId,
      session_id: sessionId,
      num_categories: numCategories,
      num_clues: numClues,
    });
  }

  private onRecv(message: string): Observable<any> {
    return new Observable((observer) => {
      this.socket.on(message, (data) => {
        observer.next(data);
      });
    });
  }

  onPlayerChange(): Observable<any> {
    return this.onRecv('players');
  }

  onHost(): Observable<any> {
    return this.onRecv('host');
  }

  onGameState(): Observable<any> {
    return this.onRecv('game_state');
  }

  onBoardData(): Observable<any> {
    return this.onRecv('board_data');
  }

  onPlayerCash(): Observable<any> {
    return this.onRecv('player_cash')
  }

  onTimerEmit(): Observable<any> {
    return this.onRecv('timer');
  }

  // Disconnect from the socket
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
}
