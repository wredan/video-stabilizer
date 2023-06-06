import { Component, OnInit } from '@angular/core';
import { WebSocketService } from 'src/app/services/websocket-service/web-socket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-processing-component',
  templateUrl: './processing-component.component.html',
  styleUrls: ['./processing-component.component.scss']
})
export class ProcessingComponent implements OnInit {
  stages: { state: string, message: string, progress: number, total: number }[] = [];
  private subscription: Subscription | undefined;

  constructor(private webSocketService: WebSocketService) { }

  ngOnInit(): void {
    this.subscription = this.webSocketService.receive().subscribe({
      next: message => { 
        console.log(message);

        let stage = this.stages.find(s => s.state === message.state);

        if (!stage) {
          stage = { state: message.state, message: message.data.message, progress: 0, total: 0 };
          this.stages.push(stage);
        }

        if (message.state === 'file_processed_success') {
          this.subscription!.unsubscribe();
        }

        if (message.data.total) {
          stage.progress = message.data.step;
          stage.total = message.data.total;
        }

        this.webSocketService.send('');
      },
      error: err => {
        console.error('WebSocket error:', err);
      }
    });
  }
}