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
  draggingOver = false;
  value: number = 40;
  isCardClosed = false;

  uploadForm = this.formBuilder.group({
    blockSize: ['64', Validators.required],
    searchRange: [16, [Validators.required, Validators.min(2), Validators.max(32)]],
    filterIntensity: [50, [Validators.required, Validators.min(0), Validators.max(100)]],
    cropFrames: [false, Validators.required],
  });

  constructor(
    private formBuilder: FormBuilder, 
    private videoService: VideoService,
    private webSocketService: WebSocketService) { }

  onSubmit() {
    if (this.uploadForm.valid && this.videoFile) {
      const formData = new FormData();
      if (this.videoFile) {
        formData.append('file', this.videoFile);
      }
      console.log(this.videoFile.name)

      this.videoService.uploadVideo(formData, this.videoFile.name).subscribe({
        next: response => {
          console.log(response)
          const filename = response.data.filename;
          this.webSocketService.connect();
          this.webSocketService.start_processing = true
          this.webSocketService.send({
            state: 'start_processing',
            data: {
              filename: filename,
              blockSize: this.uploadForm.value.blockSize,
              searchRange: this.uploadForm.value.searchRange,
              filterIntensity: this.uploadForm.value.filterIntensity,
              cropFrames: this.uploadForm.value.cropFrames,
            },
          });
        },
        error: err => {console.log(err)}
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
        console.error('File is not a video');
        // Show an error message to the user
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

      // Show video preview
      const reader = new FileReader();
      reader.onload = (e: any) => this.videoUrl = e.target.result;
      if (this.videoFile) {
        reader.readAsDataURL(this.videoFile);
      }      
    }
  }
  

  onFileChange(file: File | Event): void {
    console.log(this.videoFile)
    let selectedFile: File | null = null;
    if (file instanceof File) {
      selectedFile = file;
    } else if (file instanceof Event && file.target instanceof HTMLInputElement) {
      selectedFile = file.target.files ? file.target.files[0] : null;
    }
  
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      this.videoFile = selectedFile;
  
      // Show video preview
      const reader = new FileReader();
      reader.onload = (e: any) => this.videoUrl = e.target.result;
      reader.readAsDataURL(this.videoFile);      
    } else {
      console.error('File is not a video');
      // Show an error message to the user
    }
  }

  formatLabel(value: number) {
    if (!value) {
      return "0";
    }
    this.value = value;
    console.log(this.value);
   
    return value.toString();
  }

  toggleCard() {
    this.isCardClosed = !this.isCardClosed;
  }
}