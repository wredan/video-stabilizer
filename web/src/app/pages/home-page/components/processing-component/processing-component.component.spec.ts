import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcessingComponentComponent } from './processing-component.component';

describe('ProcessingComponentComponent', () => {
  let component: ProcessingComponentComponent;
  let fixture: ComponentFixture<ProcessingComponentComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ProcessingComponentComponent]
    });
    fixture = TestBed.createComponent(ProcessingComponentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
