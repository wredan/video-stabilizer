import { HttpEventType, HttpResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { NotificationService } from 'src/app/services/notification-service/notification.service';
import { VideoService } from 'src/app/services/video-service/video-service.service';
import { WebSocketService } from 'src/app/services/websocket-service/web-socket.service';
import { environment } from 'src/environments/environment';

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
    motionEstimationMethod: [environment.defaultFormValues.motionEstimationMethod, Validators.required],
    ofMotionType: [environment.defaultFormValues.ofMotionType, Validators.required],
    blockSize: [environment.defaultFormValues.blockSize, Validators.required],
    searchRange: [
      environment.defaultFormValues.searchRange,
      [Validators.required, Validators.min(2), Validators.max(32)],
    ],
    filterIntensity: [
      environment.defaultFormValues.filterIntensity,
      [Validators.required, Validators.min(0), Validators.max(100)],
    ],
    cropFrames: [environment.defaultFormValues.cropFrames, Validators.required],
    compareMotion: [environment.defaultFormValues.compareMotion, Validators.required],
  });

  downloadCompIsVisible: boolean = false

  constructor(
    private formBuilder: FormBuilder,
    private videoService: VideoService,
    public webSocketService: WebSocketService,
    private notificationService: NotificationService 
  ) {}

  onMethodChange(value: string) {
    if (value === 'BLOCK_MATCHING') {
      this.uploadForm.controls['blockSize'].setValue(environment.defaultFormValues.blockSize);
      this.uploadForm.controls['searchRange'].setValue(environment.defaultFormValues.searchRange);
    } else if (value === 'OPTICAL_FLOW') {
      this.uploadForm.controls['ofMotionType'].setValue(environment.defaultFormValues.ofMotionType);
    }
  }  

  reset() {
    // Reset the form
    this.uploadForm.reset({
      motionEstimationMethod: environment.defaultFormValues.motionEstimationMethod,
      ofMotionType: environment.defaultFormValues.ofMotionType,
      blockSize: environment.defaultFormValues.blockSize,
      searchRange: environment.defaultFormValues.searchRange,
      filterIntensity: environment.defaultFormValues.filterIntensity,
      cropFrames: environment.defaultFormValues.cropFrames,
      compareMotion: environment.defaultFormValues.compareMotion
    });

    // Reset other variables
    if(this.videoUrl) URL.revokeObjectURL(this.videoUrl)
    this.videoFile = undefined;
    this.videoUrl = undefined;
    this.draggingOver = false;
    this.webSocketService.start_processing = false;
    this.downloadCompIsVisible = false;
    this.uploadProgress = 0;
  }

  onSubmit() {
    if (this.uploadForm.valid && this.videoFile) {
      const formData = new FormData();
      if (this.videoFile) {
        formData.append('file', this.videoFile);
      }
      this.webSocketService.start_processing = false;
      this.webSocketService.processing = true;
      this.downloadCompIsVisible = false

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
                motion_estimation_method: this.uploadForm.value.motionEstimationMethod,
                stabilization_parameters: {
                  motion_estimation: {
                    block_matching: {
                      block_size: this.uploadForm.value.blockSize,
                      search_range: this.uploadForm.value.searchRange,
                    },
                    optical_flow: this.getOfParams(this.uploadForm.value.ofMotionType!)
                  },
                  filter_intensity: this.uploadForm.value.filterIntensity,
                  crop_frames: this.uploadForm.value.cropFrames,
                  compare_motion: this.uploadForm.value.compareMotion
                },
              },
            });
            this.videoService.compare_motion_request = this.uploadForm.value.compareMotion!            
          }
        },
        error: (err) => {
          console.error(err);
          this.webSocketService.start_processing = false
          this.webSocketService.processing = false;
          this.notificationService.showError("An error during uploading occurred.")
          this.reset()
        },
      });
    } else {
      this.notificationService.showError("You need to choose a file before uploading anything!")
    }
  }
  
  getOfParams(index: string) {
    switch(index){
      case '0': return environment.opticalFlowParams[0];
      case '1': return environment.opticalFlowParams[1];
      default: return null;
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
