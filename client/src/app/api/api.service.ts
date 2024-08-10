import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private apiUrl = environment.backendURL;

  constructor(private http: HttpClient) {}

  createRoomId(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/create_room_id`);
  }

  getSession(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/get_session`);
  }

  createSession(room_id: string, username: string): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/api/create_session?room_id=${room_id}&username=${username}`
    );
  }

  validRoom(room_id: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/valid_room?room_id=${room_id}`);
  }

  isHost(sessionId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/is_host?session_id=${sessionId}`);
  }
}
