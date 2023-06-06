import { Component, OnInit } from '@angular/core';
import { VideoService } from 'src/app/services/video-service/video-service.service';
import { WebSocketService } from 'src/app/services/websocket-service/web-socket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-download-component',
  templateUrl: './download-component.component.html',
  styleUrls: ['./download-component.component.scss']
})
export class DownloadComponent implements OnInit {
  filename: string | null = null;
  videoUrl: string | null = null; 
  private subscription: Subscription | undefined;
  
  constructor(private videoService: VideoService, private webSocketService: WebSocketService) { }

  ngOnInit(): void {
    this.subscription = this.webSocketService.receive().subscribe({
      next: message => {
        if (message.state === 'file_processed_success') {
          this.filename = message.data.filename;
          this.downloadFile();
          this.subscription!.unsubscribe();
        }
      },
      error: err => {
        console.error('WebSocket error:', err);
      }
    });
  }

  downloadFile(): void {
    if (this.filename) {
      this.videoService.downloadVideo(this.filename).subscribe({
        next: blob => {
          this.videoUrl = window.URL.createObjectURL(blob); 
          // const link = document.createElement('a');
          // link.href = this.videoUrl;
          // link.download = this.filename!;
          // link.click();
          // window.URL.revokeObjectURL(this.videoUrl);
          this.deleteFiles();
        },
        error: err => {
          console.error('Download error:', err);
        }
      });
    }
  }

  deleteFiles(): void {
    this.videoService.deleteFiles().subscribe({
      next: response => {
        console.log('Files deleted successfully');
        this.webSocketService.close();
      },
      error: err => {
        console.error('Delete files error:', err);
      }
    });
  }
}
