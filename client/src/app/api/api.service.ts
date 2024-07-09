import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  createRoomId(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/create_room_id`);
  }

  getSession(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/get_session`);
  }

  createSession(room_id : string): Observable<any> {
    return this.http.get(`${this.apiUrl}/api/create_session?room_id=${room_id}`);
  }

  validRoom(room_id : string) : Observable<any> {
    return this.http.get(`${this.apiUrl}/api/valid_room?room_id=${room_id}`);
  }
}
