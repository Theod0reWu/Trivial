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
  constructor(private elementRef: ElementRef, private socketService: SocketService) {}
  // constructor(private elementRef: ElementRef, private apiService: ApiService) {}
  @ViewChild('bgOver') bgOverlay!: ElementRef;
  pageStates = PageStates;
  title = 'client';

  state = this.pageStates.Landing;
  roomId = '';
  host = null;

  // private socketService = null;

  ngOnInit() : void {
    

  }

  handleChangeState(data: any) {
    switch (data.state) {
      case PageStates.Landing: {
        this.state = this.pageStates.Landing;
        setTimeout(() => {
          this.bgOverlay.nativeElement.classList.remove('bg-rendered');
        }, 10);
        break;
      }
      case PageStates.Waiting: {
        this.roomId = data.roomId;

        // setup socket connection
        // var session_obs = this.apiService.getSession();
        // session_obs.subscribe(result => {
        //   if (result.reconnect) {
        //             // joinRoom(result.room_id);
        //         }
        // })
        // this.socketService = 

        this.state = this.pageStates.Waiting;
        this.host = data.host;
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
