import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { Component, Input, ViewEncapsulation, inject } from '@angular/core';
import {
  MatChipEditedEvent,
  MatChipInputEvent,
  MatChipsModule,
} from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { LiveAnnouncer } from '@angular/cdk/a11y';

export interface Category {
  name: string;
}

@Component({
  selector: 'waiting-taglist',
  templateUrl: '../components_html/waiting_taglist.component.html',
  styleUrl: '../components_css/waiting_taglist.component.css',
  standalone: true,
  imports: [MatFormFieldModule, MatChipsModule, MatIconModule],
  encapsulation: ViewEncapsulation.None,
})
export class WaitingTaglist {
  addOnBlur = true;
  readonly separatorKeysCodes = [ENTER, COMMA] as const;
  @Input() categories!: Category[];

  announcer = inject(LiveAnnouncer);

  add(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    if (value) {
      this.categories.push({ name: value });
    }
    event.chipInput!.clear();
  }

  remove(category: Category): void {
    const index = this.categories.indexOf(category);
    if (index >= 0) {
      this.categories.splice(index, 1);
      this.announcer.announce(`Removed ${category}`);
    }
  }

  edit(category: Category, event: MatChipEditedEvent) {
    const value = event.value.trim();
    if (!value) {
      this.remove(category);
      return;
    }
    const index = this.categories.indexOf(category);
    if (index >= 0) {
      this.categories[index].name = value;
    }
  }
}
