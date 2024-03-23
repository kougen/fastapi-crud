import os
import sys
from pathlib import Path
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn
from typing import List, Optional
from pyrepositories import JsonTable, DataSource, Entity, IdTypes


path_root = Path(__file__).parents[1]
sys.path.append(os.path.join(path_root, 'src'))

from crud import CRUDApi, Model, EntityFactory


class Organizer(Model):
    email: str


class Joiner(Model):
    name: str
    company: str


class Event(Model):
    date: str
    organizer: Organizer
    status: str
    max_attendees: int
    joiners: Optional[List[Joiner]] = None


class EventEntity(Entity):
    @property
    def date(self):
        return self.fields.get("date")
    @date.setter
    def date(self, value):
        self.fields["date"] = value
    @property
    def organizer(self):
        return self.fields.get("organizer")
    @organizer.setter
    def organizer(self, value):
        self.fields["organizer"] = value
    @property
    def status(self):
        return self.fields.get("status")
    @status.setter
    def status(self, value):
        self.fields["status"] = value
    @property
    def max_attendees(self):
        return self.fields.get("max_attendees")
    @max_attendees.setter
    def max_attendees(self, value):
        self.fields["max_attendees"] = value
    @property
    def joiners(self):
        return self.fields.get("joiners") or []
    @joiners.setter
    def joiners(self, value):
        self.fields["joiners"] = value



app = FastAPI()

ds = DataSource(id_type=IdTypes.UUID)
t = JsonTable("event", os.path.join(path_root, "data"))
filters = { "date": (str, ""), "organizer": (str, ""), "status": (str, ""), "event_type": (str, ""), } 
t.set_filter_fields(filters)

ds.add_table(t)
api = CRUDApi(ds, app)

router = api.register_router("event" , Event).get_base()

@router.get("/test", tags=["event"])
def test():
    return "test"

api.publish()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1112)


