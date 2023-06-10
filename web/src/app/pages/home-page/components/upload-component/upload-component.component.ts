import { HttpEventType, HttpResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { NotificationService } from 'src/app/services/notification-service/notification.service';
import { VideoService } from 'src/app/services/video-service/video-service.service';
import { WebSocketService } from 'src/app/services/websocket-service/web-socket.service';
@Component({
  selector: 'app-upload-component',
  templateUrl: './upload-component.component.html',
  styleUrls: ['./upload-component.component.scss'],
})
export class UploadComponent {
  videoFile: File | undefined;
  videoUrl: string | undefined;
  draggingOver = false;
  uploadProgress: number = 0;
  private subscription: Subscription | undefined;

  videoPlayerOption: any;

  uploadForm = this.formBuilder.group({
    blockSize: ['64', Validators.required],
    searchRange: [
      16,
      [Validators.required, Validators.min(2), Validators.max(32)],
    ],
    filterIntensity: [
      40,
      [Validators.required, Validators.min(0), Validators.max(100)],
    ],
    cropFrames: [false, Validators.required],
    compareMotion: [false, Validators.required],
  });

  downloadCompIsVisible: boolean = false

  constructor(
    private formBuilder: FormBuilder,
    private videoService: VideoService,
    public webSocketService: WebSocketService,
    private notificationService: NotificationService 
  ) {}

  reset() {
    // Reset the form
    this.uploadForm.reset({
      blockSize: '64',
      searchRange: 16,
      filterIntensity: 40,
      cropFrames: false,
      compareMotion: false
    });

    // Reset other variables
    URL.revokeObjectURL(this.videoUrl!)
    this.videoFile = undefined;
    this.videoUrl = undefined;
    this.draggingOver = false;
    this.webSocketService.start_processing = false;
    this.downloadCompIsVisible = false;
    this.webSocketService.end_processing = false;
    this.uploadProgress = 0;
  }

  onSubmit() {
    if (this.uploadForm.valid && this.videoFile) {
      const formData = new FormData();
      if (this.videoFile) {
        formData.append('file', this.videoFile);
      }

      this.videoService.uploadVideo(formData, this.videoFile.name).subscribe({
        next: (event) => {
          if (event.type === HttpEventType.UploadProgress) {
            // Calculate and update progress
            this.uploadProgress = Math.round(
              (100 * event.loaded) / event.total
            );
          } else if (event instanceof HttpResponse) {
            this.notificationService.showSuccess("File uploaded! Starting processing...", 3000)
            this.uploadProgress = 0;
            const filename = event.body.data.filename;
            this.webSocketService.connect();
            this.webSocketService.start_processing = true;
            setTimeout(() => {
              this.downloadCompIsVisible = true;
            }, 1000); 
            this.webSocketService.send({
              state: 'start_processing',
              data: {
                filename: filename,
                stabilization_parameters: {
                  block_size: this.uploadForm.value.blockSize,
                  search_range: this.uploadForm.value.searchRange,
                  filter_intensity: this.uploadForm.value.filterIntensity,
                  crop_frames: this.uploadForm.value.cropFrames,
                  compare_motion: this.uploadForm.value.compareMotion
                },
              },
            });
            this.videoService.compare_motion_request = this.uploadForm.value.compareMotion!
            this.subscription = this.webSocketService.receive().subscribe({
               error: err => {
                this.reset();
                this.subscription?.unsubscribe()
              }
            });
          }
        },
        error: (err) => {
          console.error(err);
          this.notificationService.showError("An error during uploading occurred.")
          this.reset()
        },
      });
    } else {
      this.notificationService.showError("You need to choose a file before uploading anything!")
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.draggingOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.draggingOver = false;
  }

  private isValidVideo(file: File): boolean {
    const fileType = file.type.split("/")[1];

    if (!file.type.startsWith('video/') || !['avi', 'mp4', 'quicktime'].includes(fileType)) {
      this.notificationService.showError("You can upload only .mp4/.avi/.MOV videos");
      return false;
    }
  
    if (fileType == "avi") {
      this.notificationService.showError(`Preview not available for ${fileType}`);
    }
  
    return true;
  }
  
  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.draggingOver = false;
    const files = event.dataTransfer?.files;
    if (!files || files.length === 0) return;
  
    const file = files[0];
  
    if (this.isValidVideo(file)) {
      this.onFileChange(file);
    }
  }
  
  onInputFileChange(event: any) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
  
    if (this.isValidVideo(file)) {
      this.videoFile = file;
      this.videoUrl = URL.createObjectURL(this.videoFile!);
    }
  }
  
  onFileChange(file: File | Event): void {
    let selectedFile: File | null = null;
    if (file instanceof File) {
      selectedFile = file;
    } else if (
      file instanceof Event &&
      file.target instanceof HTMLInputElement
    ) {
      selectedFile = file.target.files ? file.target.files[0] : null;
    }
  
    if (selectedFile && this.isValidVideo(selectedFile)) {
      this.videoFile = selectedFile;
      this.videoUrl = URL.createObjectURL(this.videoFile);
    }
  }
  
  
}
