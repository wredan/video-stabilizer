import { HttpEventType, HttpResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
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

  videoPlayerOption: any;

  uploadForm = this.formBuilder.group({
    blockSize: ['64', Validators.required],
    searchRange: [
      16,
      [Validators.required, Validators.min(2), Validators.max(32)],
    ],
    filterIntensity: [
      50,
      [Validators.required, Validators.min(0), Validators.max(100)],
    ],
    cropFrames: [false, Validators.required],
  });

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
      filterIntensity: 50,
      cropFrames: false,
    });

    // Reset other variables
    URL.revokeObjectURL(this.videoUrl!)
    this.videoFile = undefined;
    this.videoUrl = undefined;
    this.draggingOver = false;
    this.webSocketService.start_processing = false;
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
            this.webSocketService.send({
              state: 'start_processing',
              data: {
                filename: filename,
                stabilization_parameters: {
                  block_size: this.uploadForm.value.blockSize,
                  search_range: this.uploadForm.value.searchRange,
                  filter_intensity: this.uploadForm.value.filterIntensity,
                  crop_frames: this.uploadForm.value.cropFrames,
                },
              },
            });
          }
        },
        error: (err) => {
          console.log(err);
          this.notificationService.showError("An error during uploading occurred.")
          this.reset()
        },
      });
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.draggingOver = true;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.draggingOver = false;
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('video/')) {
        this.onFileChange(file);
      } else {
        this.notificationService.showError("File is not a video. You can upload only .mp4/.avi/.MOV videos")
      }
    }
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.draggingOver = false;
  }

  onInputFileChange(event: any) {
    if (event.target.files && event.target.files[0]) {
      this.videoFile = event.target.files[0];
      if (this.videoFile && this.videoFile.type.startsWith('video/')) {
          this.videoUrl = URL.createObjectURL(this.videoFile);       
      }  else {
        this.notificationService.showError("File is not a video. You can upload only .mp4/.avi/.MOV videos")
      }  
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

    if (selectedFile && selectedFile.type.startsWith('video/')) {
      this.videoFile = selectedFile;

      // Show video preview
      this.videoUrl = URL.createObjectURL(this.videoFile);
    } else {
      this.notificationService.showError("File is not a video. You can upload only .mp4/.avi/.MOV videos")
    }
  }
  
}
