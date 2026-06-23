import { Entity } from "./entity.js";
import { Identifier } from "./identifier.js";
import { DomainEvent } from "./domain-event.js";

export abstract class AggregateRoot<TId extends Identifier> extends Entity<TId> {
  private _events: DomainEvent[] = [];

  protected addEvent(event: DomainEvent): void {
    this._events.push(event);
  }

  clearEvents(): DomainEvent[] {
    const events = [...this._events];
    this._events = [];
    return events;
  }
}
