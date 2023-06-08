import { Component, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { VideoService } from 'src/app/services/video-service/video-service.service';
import { WebSocketService } from 'src/app/services/websocket-service/web-socket.service';
import { MatDialog } from '@angular/material/dialog';
import { ImageDialogComponent } from '../image-dialog/image-dialog.component';
import { NotificationService } from 'src/app/services/notification-service/notification.service';

@Component({
  selector: 'app-stats-download',
  templateUrl: './stats-download.component.html',
  styleUrls: ['./stats-download.component.scss']
})
export class StatsDownloadComponent implements OnInit {
  private subscription: Subscription | undefined;
  title: string | undefined = "Processing the video...";
  afpUrl: string | null = null; 
  gcmUrl: string | null = null; 

  constructor(
    private videoService: VideoService, 
    private webSocketService: WebSocketService,
    private notificationService : NotificationService,
    public dialog: MatDialog) { }

  ngOnInit(): void {
    this.subscription = this.webSocketService.receive().subscribe({
      next: message => {
        if (message.state === 'file_processed_success') {
          this.downloadFiles();
          this.subscription!.unsubscribe();
        }
      },
      error: err => {
        console.error('WebSocket error:', err);
        this.notificationService.showError("Connection error has occurred.")
      }
    });
  }

  downloadFiles(): void {
      this.videoService.downloadImage("absolute_frame_position.png").subscribe({
        next: blob => {
          this.afpUrl = window.URL.createObjectURL(blob); 
        },
        error: err => {
          console.error('Download error:', err);
          this.notificationService.showError("Download error has occurred.")
        }
      });
      this.videoService.downloadImage("global_corrected_motion_vectors.png").subscribe({
        next: blob => {
          this.gcmUrl = window.URL.createObjectURL(blob); 
        },
        error: err => {
          console.error('Download error:', err);
          this.notificationService.showError("Download error has occurred.")
        }
      });
  }

  openDialog(imageUrl: string): void {
      this.dialog.open(ImageDialogComponent, {
        data: { url: imageUrl },
        panelClass: 'full-screen-dialog'
      });
  }
}