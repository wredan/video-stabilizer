import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './pages/home-page/home-page.component';
import { UploadComponent } from './pages/home-page/components/upload-component/upload-component.component';
import { ProcessingComponent } from './pages/home-page/components/processing-component/processing-component.component';

import { VideoService } from './services/video-service/video-service.service';
import { WebSocketService } from './services/websocket-service//web-socket.service';
import { DownloadComponent } from './pages/home-page/components/download-component/download-component.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatSliderModule } from '@angular/material/slider';
import {MatIconModule} from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    UploadComponent,
    ProcessingComponent,
    DownloadComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule,
    BrowserAnimationsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatSidenavModule,
    MatSliderModule,
    MatIconModule,
    MatProgressBarModule
  ],
  providers: [VideoService, WebSocketService],
  bootstrap: [AppComponent]
})
export class AppModule { }
