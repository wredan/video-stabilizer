import { Injectable } from '@angular/core';
import { MatSnackBar, MatSnackBarHorizontalPosition, MatSnackBarVerticalPosition } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {

  horizontalPosition: MatSnackBarHorizontalPosition = 'right';
  verticalPosition: MatSnackBarVerticalPosition = 'top';

  constructor(private snackBar: MatSnackBar) { }

  showSuccess(message: string, duration: number = 5000): void {
    this.snackBar.open(message, '', { 
      duration: duration, 
      panelClass: ['app-notification-success'],
      horizontalPosition: this.horizontalPosition,
      verticalPosition: this.verticalPosition
    });
  }
  
  showError(message: string, duration: number = 5000): void {
    this.snackBar.open(message, '', { 
      duration: duration, 
      panelClass: ['app-notification-error'],
      horizontalPosition: this.horizontalPosition,
      verticalPosition: this.verticalPosition
    });
  }

}