import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from pyrepositories import JsonTable, DataSource, Entity, IdTypes, FieldBase, FieldKeyTypes, FieldTypes

from pyrepositories import JsonTable, DataSource, Entity, IdTypes
import uvicorn

path_root = Path(__file__).parents[1]
sys.path.append(os.path.join(path_root, 'src'))

from crud import CRUDApi, Model, EntityFactory, AuthConfig, UserEntity, USER_FIELDS


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
        return self.get_field("date")
    @date.setter
    def date(self, value):
        self.set_field_value("date", value)
    @property
    def organizer(self):
        return self.get_field("organizer")
    @organizer.setter
    def organizer(self, value):
        self.set_field_value("organizer", value)
    @property
    def status(self):
        return self.get_field("status")
    @status.setter
    def status(self, value):
        self.set_field_value("status", value)
    @property
    def max_attendees(self):
        return self.get_field("max_attendees")
    @max_attendees.setter
    def max_attendees(self, value):
        self.set_field_value("max_attendees", value)
    @property
    def joiners(self):
        return self.get_field("joiners")
    @joiners.setter
    def joiners(self, value):
        self.set_field_value("joiners", value)



app = FastAPI()

def get_dummy_users_db():
    tbl = JsonTable("users", os.path.join(path_root, "data"), USER_FIELDS)
    tbl.clear()
    # tbl.set_filter_fields({ "username": (str, ""), "email": (str, ""), "full_name": (str, ""), "disabled": (bool, False) })
    users = []
    users.append(UserEntity("jonhdoe", "john@doe.com", "John Doe"))
    users.append(UserEntity("janedoe", "jane@doe.com", "Jane Doe"))
    for user in users:
        tbl.insert(user)

    return tbl

ds = DataSource(id_type=IdTypes.UUID)

fields = [
    FieldBase("date", FieldTypes.STR, FieldKeyTypes.PRIMARY),
    FieldBase("organizer", FieldTypes.STR, FieldKeyTypes.REQUIRED),
    FieldBase("status", FieldTypes.STR, FieldKeyTypes.REQUIRED),
    FieldBase("max_attendees", FieldTypes.INT, FieldKeyTypes.REQUIRED),
    FieldBase("joiners", FieldTypes.LIST, FieldKeyTypes.OPTIONAL, [])
]

t = JsonTable("event", os.path.join(path_root, "data"), fields)
filters = [
    FieldBase("date", FieldTypes.STR, FieldKeyTypes.OPTIONAL, ""),
    FieldBase("organizer", FieldTypes.STR, FieldKeyTypes.OPTIONAL, ""),
    FieldBase("status", FieldTypes.STR, FieldKeyTypes.OPTIONAL, ""),
    FieldBase("event_type", FieldTypes.STR, FieldKeyTypes.OPTIONAL, ""),
]
# This will be used to generate the query parameters
# filters = { "date": (str, ""), "organizer": (str, ""), "status": (str, ""), "event_type": (str, ""), } 

ds.add_table(t)
api = CRUDApi(ds, app, authConfig)

router = api.register_router("event" , Event, filters=filters).get_base()

@router.get("/test", tags=["event"])
def test():
    return "test"

api.publish()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1112)


