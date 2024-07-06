import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  private socket: Socket;

  constructor() {
    // FastAPI server url
    this.socket = io('http://localhost:8000');
    this.socket.on("connect", () => {
      console.log("Connected to server");
    });
  }

  // Emit an event to join a room
  joinRoom(room: string): void {
    this.socket.emit('join_room', { room });
  }

  // Emit an event to leave a room
  leaveRoom(room: string): void {
    this.socket.emit('leave_room', { room });
  }

  // Emit an event to send a message
  sendBoardSize(room: string, categories: number, clues : number): void {
    this.socket.emit('board_size', { room, categories, clues});
  }

  // Emit an event to send a game action
  sendGameAction(room: string, action: any): void {
    this.socket.emit('game_action', { room, action });
  }

  // Listen for messages from the server
  onMessage(): Observable<any> {
    return new Observable(observer => {
      this.socket.on('message', (data) => {
        observer.next(data);
      });
    });
  }

  // Listen for game state updates from the server
  onGameState(): Observable<any> {
    return new Observable(observer => {
      this.socket.on('game_state', (state) => {
        observer.next(state);
      });
    });
  }

  // Disconnect from the socket
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
}
