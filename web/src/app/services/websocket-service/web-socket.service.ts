import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket$: WebSocketSubject<any> | undefined;

  private webSocketUrl = environment.webSocketUrl;
  
  public start_processing = false

  public connect(): void {
    if (!this.socket$ || this.socket$.closed) {
      this.socket$ = webSocket(this.webSocketUrl);
    }
  }

  public send(data: any): void {
    if (this.socket$) {
      this.socket$.next(data);
    } else {
      console.error('Must connect to WebSocket before sending data');
    }
  }

  public close(): void {
    if (this.socket$) {
      this.socket$.complete();
    }
  }

  public receive(): Observable<any> {
    return this.messages$;
  }  

  public get messages$() {
    return this.socket$!.asObservable();
  }
}