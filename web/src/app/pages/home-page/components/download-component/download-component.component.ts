import { Component, OnInit, OnDestroy } from '@angular/core';
import { VideoService } from 'src/app/services/video-service/video-service.service';
import { WebSocketService } from 'src/app/services/websocket-service/web-socket.service';
import { Subscription } from 'rxjs';
import { NotificationService } from 'src/app/services/notification-service/notification.service';

@Component({
  selector: 'app-download-component',
  templateUrl: './download-component.component.html',
  styleUrls: ['./download-component.component.scss']
})
export class DownloadComponent implements OnInit, OnDestroy {
  filename: string | null = null;
  videoUrl: string | null = null; 
  private subscription: Subscription | undefined;
  title: string | undefined = "Processing the video...";
  
  constructor(
    private videoService: VideoService, 
    private webSocketService: WebSocketService,
    private notificationService : NotificationService) { }

  ngOnInit(): void {
    this.subscription = this.webSocketService.receive().subscribe({
      next: message => {
        if (message.state === 'file_processed_success') { 
          this.filename = message.data.filename; 
          this.title = "Downloading the video..."      
          this.downloadFile();          
          this.subscription!.unsubscribe();
        }
      },
      error: err => {
        console.error('WebSocket error:', err);
        this.notificationService.showError("Connection error has occurred. Please reload the webpage.")
      }
    });
  }

  ngOnDestroy(): void {
    URL.revokeObjectURL(this.videoUrl!)
  }

  downloadFile(): void {
    if (this.filename) {
      this.videoService.downloadVideo(this.filename).subscribe({
        next: blob => {
          this.videoUrl = URL.createObjectURL(blob);
          this.title = "Stabilized video ready - "
          this.deleteFiles();
          this.webSocketService.processing = false   
        },
        error: err => {
          console.error('Download error:', err);
          this.notificationService.showError("Download error has occurred.")
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
        this.notificationService.showError("Delete files error has occurred.")
      }
    });
  }
}
