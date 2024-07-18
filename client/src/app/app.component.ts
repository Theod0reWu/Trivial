import { AfterViewInit, Component, ElementRef, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LandingComponent } from './components/landing.component';
import { WaitingComponent } from './components/waiting.component';
import { GameComponent } from './components/game.component';
import { LoadingComponent } from './components/loading.component';
import { ConnectorService } from './api/connector.service';
import { GameData } from './api/GameData';

export enum PageStates {
  Landing,
  About,
  Waiting,
  Loading,
  InGame,
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    LandingComponent,
    WaitingComponent,
    GameComponent,
    LoadingComponent,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  // constructor(private elementRef: ElementRef, private socketService: SocketService) {}
  constructor(
    private elementRef: ElementRef,
    public connectorService: ConnectorService,
    public gameData: GameData
  ) {}
  @ViewChild('bgOver') bgOverlay!: ElementRef;
  pageStates = PageStates;
  title = 'client';
  loadingMessage = '';

  state = this.pageStates.Landing;

  ngOnInit(): void {
    // handle reconnecting from a disconnect
  }

  updateAndConnect(data: any): void {
    /*
      Updates the member variables based on data from the landing page and establishes the connecter
    */

    //update connector
    this.connectorService.setHost(data.host);
    this.connectorService.setUsername(data.username);
    this.connectorService.setRoom(data.roomId);

    // The roomid has been generated we can now connect with sockets.
    const callback = () => {
      this.connectorService.gameStateChange$.subscribe({
        next: (value) => {
          if (value === 'board') {
            this.state = this.pageStates.InGame;
            this.connectorService.loading = false;
          } else if (value === 'generating') {
            this.state = this.pageStates.Loading;
            this.loadingMessage =
              '<b>Hang tight!</b> Generating your clues. This may take a while.';
            this.connectorService.loading = true;
          }
        },
      });
    };
    this.connectorService.connectToRoom(callback);
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
      case PageStates.Loading: {
        this.state = this.pageStates.Loading;
        this.gameData.numCategories = data.numCategories;
        this.gameData.numClues = data.numClues;
        this.loadingMessage = data.loadingMessage;

        this.connectorService.startGame(
          this.gameData.numCategories,
          this.gameData.numClues
        );
        break;
      }
    }
    window.scrollTo(0, 0);
  }
}
