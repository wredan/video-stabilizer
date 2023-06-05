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

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    UploadComponent,
    ProcessingComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule
  ],
  providers: [VideoService, WebSocketService],
  bootstrap: [AppComponent]
})
export class AppModule { }
