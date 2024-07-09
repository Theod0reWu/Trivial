import { AfterViewInit, Component, ElementRef, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LandingComponent } from './components/landing.component';
import { WaitingComponent } from './components/waiting.component';
import { GameComponent } from './components/game.component';
import { ConnectorService } from './api/connector.service';

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
  constructor(private elementRef: ElementRef, public connectorService: ConnectorService) {}
  @ViewChild('bgOver') bgOverlay!: ElementRef;
  pageStates = PageStates;
  title = 'client';

  state = this.pageStates.Landing;

  ngOnInit() : void {
    // handle reconnecting from a disconnect

  }

  updateAndConnect(data: any) : void {
    /*
      Updates the member variables based on data from the landing page and establishes the connecter
    */

    //update connector
    this.connectorService.setHost(data.host);
    this.connectorService.setUsername(data.username);
    this.connectorService.setRoom(data.roomId);


    // The roomid has been generated we can now connect with sockets.
    this.connectorService.connectToRoom();
  }

  handleChangeState(data: any) {
    switch (data.state) {
      case PageStates.Landing: {
        //left the room disconnect socket
        this.connectorService.disconnectFromRoom();

        this.state = this.pageStates.Landing;
        setTimeout(() => {
          this.bgOverlay.nativeElement.classList.remove('bg-rendered');
        }, 10);
        break;
      }
      case PageStates.Waiting: {
        this.updateAndConnect(data);
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
