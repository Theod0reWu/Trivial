import {
  AfterViewInit,
  Component,
  ElementRef,
  Inject,
  ViewChild,
} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LandingComponent } from './components/landing.component';
import { WaitingComponent } from './components/waiting.component';
import { GameComponent } from './components/game.component';
import { LoadingComponent } from './components/loading.component';
import { ConnectorService } from './api/connector.service';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogModule,
} from '@angular/material/dialog';
import { NgIf } from '@angular/common';

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
    NgIf,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  constructor(
    public dialog: MatDialog,
    public connectorService: ConnectorService
  ) {}
  @ViewChild(GameComponent) gameComponent: GameComponent;
  @ViewChild('bgOver') bgOverlay!: ElementRef;

  loadingMessage = '';

  pageStates = PageStates;
  state = this.pageStates.Landing;

  // function to dynamically change font size based on container
  changeFontSize = (ref: ElementRef) => {
    const isOverflown = (element: any) => {
      return (
        element &&
        (element.scrollHeight > element.clientHeight ||
          element.scrollWidth > element.clientWidth)
      );
    };
    let fontSize = parseInt(
      getComputedStyle(ref.nativeElement).getPropertyValue('font-size')
    );
    let overflow = isOverflown(ref.nativeElement);

    if (overflow) {
      // shrink text
      for (let i = fontSize; i > 1; --i) {
        if (overflow) {
          --fontSize;
          ref.nativeElement.style.fontSize = fontSize + 'px';
        }
        overflow = isOverflown(ref.nativeElement);
      }
    } else {
      // grow text
      while (!overflow) {
        ++fontSize;
        ref.nativeElement.style.fontSize = fontSize + 'px';
        overflow = isOverflown(ref.nativeElement);
      }
      --fontSize;
      ref.nativeElement.style.fontSize = fontSize + 'px';
    }
  };

  // open modal
  openDialog(isLeaving: boolean) {
    const data = isLeaving
      ? {
          onClickLeaveGame: () =>
            this.handleChangeState({ state: PageStates.Landing }),
          title: 'Are you sure you want to leave?',
          content: 'NOTE: All player data for this game session will be lost!',
        }
      : {
          onClickLeaveGame: undefined,
          title: 'Screen size too big?',
          content: 'Use Ctrl-/Cmd- to zoom out!',
        };
    const dialogRef = this.dialog.open(InGameModal, {
      data: data,
    });
  }

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
          } else if (value === 'loading') {
            this.state = this.pageStates.Loading;
            this.loadingMessage =
              '<b>Hang tight!</b> Generating your clues. This may take a while.';
            this.connectorService.loading = true;
          }
        },
      });

      this.connectorService.pickingChange$.subscribe({
        next: (value) => {
          this.connectorService.gameData.answering = false;
          this.gameComponent.startFlickerClue(
            value['category_idx'],
            value['clue_idx'],
            value['duration']
          );
        },
      });

      this.connectorService.clueChange$.subscribe({
        next: (value) => {
          this.connectorService.gameData.current_clue = value['clue'];
          this.connectorService.gameData.buzz_in_duration = value['duration'];
          this.gameComponent.startProgressBar(value['duration']);
        },
      });

      this.connectorService.pausedChange$.subscribe({
        next: (value) => {
          if (value['action'] === 'start') {
            this.connectorService.gameData.answeringIndex = value['who'];
            if (!this.connectorService.gameData.answering) {
              this.gameComponent.otherAnswering();
            }

            this.gameComponent.pauseProgressBar();
            this.gameComponent.startAnsweringTimer(value['duration']);
          } else if (value['action'] === 'stop') {
            //stop pausing go back to buzzer page and resume the progress bar
            this.gameComponent.gameData.answering = false;
            this.gameComponent.unpause(value['duration']);
          }
        },
      });

      this.connectorService.answeringChange$.subscribe({
        next: (value) => {
          this.connectorService.gameData.answering = true;
          this.gameComponent.startAnswering(value['duration']);
        },
      });

      this.connectorService.responseChange$.subscribe({
        next: (value) => {
          if ('end' in value) {
            this.gameComponent.displayCorrectAnswer(value['answer']);
          } else {
            this.gameComponent.handleResponse(
              value['correct'],
              value['answer']
            );
          }
        },
      });

      this.connectorService.waitingChange$.subscribe({
        next: (value) => {
          this.state = this.pageStates.Waiting;
        },
      });
    };
    this.connectorService.connectToRoom(callback);
  }

  handleChosenClue(data: any) {
    this.connectorService.sendBoardChoice(data.category, data.clue);
  }

  handleBuzzIn(): void {
    this.connectorService.sendBuzzIn();
  }

  handleAnswer(ans: string) {
    this.connectorService.sendAnswer(ans);
  }

  handleToWaiting() {
    this.connectorService.sendToWaiting();
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
        this.connectorService.gameData.numCategories = data.numCategories;
        this.connectorService.gameData.numClues = data.numClues;
        this.loadingMessage = data.loadingMessage;
        this.connectorService.gameData.givenCategories = [];
        for (let i of data.categories) {
          this.connectorService.gameData.givenCategories.push(i['name']);
        }

        this.connectorService.startGame(
          this.connectorService.gameData.numCategories,
          this.connectorService.gameData.numClues,
          this.connectorService.gameData.givenCategories
        );
        break;
      }
    }
    window.scrollTo(0, 0);
  }
}

@Component({
  selector: 'in-game-modal',
  imports: [MatDialogModule],
  templateUrl: './components_html/modal.component.html',
  styleUrl: './components_css/modal.component.css',
  standalone: true,
})
export class InGameModal {
  constructor(
    @Inject(MAT_DIALOG_DATA)
    public data: {
      onClickLeaveGame: () => void;
      title: string;
      content: string;
    }
  ) {}
}
