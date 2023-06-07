import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class VideoService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  uploadVideo(formData: FormData, filename: string): Observable<any> {
    const httpOptions = {
      reportProgress: true,
      observe: 'events' as 'body'
    };
    
    return this.http.post(`${this.apiUrl}/upload/${filename}`, formData, httpOptions);
  }  

  downloadVideo(filename: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/download/${filename}`, { responseType: 'blob' });
  }

  downloadImage(filename: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/download/${filename}`, { responseType: 'blob' });
  }

  deleteFiles(): Observable<any> {
    return this.http.get(`${this.apiUrl}/delete-files`);
  }
}