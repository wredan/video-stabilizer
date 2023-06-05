import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { VideoService } from 'src/app/services/video-service/video-service.service';
import { WebSocketService } from 'src/app/services/websocket-service/web-socket.service';

@Component({
  selector: 'app-upload-component',
  templateUrl: './upload-component.component.html',
  styleUrls: ['./upload-component.component.scss']
})
export class UploadComponent {
  videoFile: File | undefined;
  videoUrl: string | undefined;

  uploadForm = this.formBuilder.group({
    blockSize: [64, Validators.required],
    searchRange: [16, [Validators.required, Validators.min(2), Validators.max(32)]],
    filterIntensity: [50, [Validators.required, Validators.min(0), Validators.max(100)]],
    cropFrames: [false, Validators.required],
  });

  constructor(
    private formBuilder: FormBuilder, 
    private videoService: VideoService,
    private webSocketService: WebSocketService) { }

  onFileChange(event: any) {
    if (event.target.files && event.target.files[0]) {
      this.videoFile = event.target.files[0];

      // Show video preview
      const reader = new FileReader();
      reader.onload = (e: any) => this.videoUrl = e.target.result;
      if (this.videoFile) {
        reader.readAsDataURL(this.videoFile);
      }      
    }
  }

  onSubmit() {
    if (this.uploadForm.valid && this.videoFile) {
      const formData = new FormData();
      if (this.videoFile) {
        formData.append('video', this.videoFile);
      }

      this.videoService.uploadVideo(formData).subscribe(
        response => {
          // Handle response
          const filename = response.data.filename;
          this.webSocketService.connect('ws://your-websocket-url.com');
          this.webSocketService.send({
            code: 'start_processing',
            data: {
              filename: filename,
              blockSize: this.uploadForm.value.blockSize,
              searchRange: this.uploadForm.value.searchRange,
              filterIntensity: this.uploadForm.value.filterIntensity,
              cropFrames: this.uploadForm.value.cropFrames,
            },
          });
        },
        error => {
          // Handle error
        }
      );   
    }
  }
}