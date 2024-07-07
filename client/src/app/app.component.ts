import { AfterViewInit, Component, ElementRef, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LandingComponent } from './components/landing.component';
import { WaitingComponent } from './components/waiting.component';
import { GameComponent } from './components/game.component';
import { SocketService } from './api/socket.service';
import { ApiService } from './api/api.service';

export enum PageStates {
  Landing,
  About,
  Waiting,
  InGame,
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, LandingComponent, WaitingComponent, GameComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  // constructor(private elementRef: ElementRef, private socketService: SocketService) {}
  constructor(private elementRef: ElementRef, private apiService: ApiService) {}
  @ViewChild('bgOver') bgOverlay!: ElementRef;
  pageStates = PageStates;
  title = 'client';

  state = this.pageStates.Landing;
  roomId: string = '';
  host: boolean = false;
  sessionId: string = '';
  username: string = '';

  private socketService: SocketService = new SocketService();

  ngOnInit() : void {
    

  }

  handleChangeState(data: any) {
    switch (data.state) {
      case PageStates.Landing: {
        //left the room disconnect socket
        this.socketService.leaveRoom(this.roomId, this.sessionId);
        this.socketService.disconnectSocket();

        // reset member variables
        this.roomId = '';
        this.host = false;
        this.sessionId = '';
        this.username= '';


        this.state = this.pageStates.Landing;
        setTimeout(() => {
          this.bgOverlay.nativeElement.classList.remove('bg-rendered');
        }, 10);
        break;
      }
      case PageStates.Waiting: {
        this.roomId = data.roomId;
        this.host = data.host;


        // The roomid has been generated we can now connect with sockets.
        // first get session_id
        this.apiService.createSession(this.roomId).subscribe( {
          next: (result) => {
            this.sessionId = result["session_id"];
            console.log("session id:", this.sessionId);
          },
          error: (err) => {
            console.error("Observable for creating a session emitted error:" + err);
          }, 
          complete: () => {
            //setup socket with sessionId and roomId
            this.socketService.initSocket(this.sessionId);
            this.socketService.joinRoom(this.roomId, this.username, this.sessionId);
          }
        });

        this.state = this.pageStates.Waiting;      
        break;
      }
      case PageStates.InGame: {
        this.state = this.pageStates.InGame;
        break;
      }
    }
    window.scrollTo(0, 0);
  }
}
