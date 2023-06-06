import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StatsDownloadComponent } from './stats-download.component';

describe('StatsDownloadComponent', () => {
  let component: StatsDownloadComponent;
  let fixture: ComponentFixture<StatsDownloadComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [StatsDownloadComponent]
    });
    fixture = TestBed.createComponent(StatsDownloadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
