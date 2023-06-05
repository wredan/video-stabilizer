import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket$: WebSocketSubject<any> | undefined;

  public connect(url: string): void {
    if (!this.socket$ || this.socket$.closed) {
      this.socket$ = webSocket(url);
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

  public get messages$() {
    return this.socket$!.asObservable();
  }
}