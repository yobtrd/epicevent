from sqlalchemy.orm import Session

from epicevent.models.event import Event


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, event: Event) -> Event:
        self.session.add(event)
        self.session.flush()
        return event
