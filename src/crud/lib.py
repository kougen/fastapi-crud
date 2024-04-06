from pydantic import BaseModel
from pyrepositories import DataTable, Entity, FieldBase, FieldTypes, FieldKeyTypes, Filter, FilterCombination, FilterCondition, FilterTypes, EntityField
from fastapi.security import OAuth2PasswordBearer


class Model(BaseModel):
    pass


def convert_field_to_filter(fields: list[FieldBase]) -> dict:
    filter_dict = {}
    for field in fields:
        if field.field_type.content_type == FieldTypes.LIST:
            raise ValueError('Field type LIST is not supported')
        if field.field_type.content_type == FieldTypes.DICT:
            raise ValueError('Field type DICT is not supported')
        filter_dict[field.name] = (field.field_type.content_type, field.default)
    return filter_dict


def convert_dict_to_filter(data: dict) -> Filter:
    conditions = []

    for key, value in data.items():
        conditions.append(FilterCondition(key, value, FilterTypes.CONTAINS))

    return Filter(conditions, FilterCombination.AND)


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def decode_token(token: str):
    return User(
        username=token + "fakedecoded", email="john@doe.com", full_name="John Doe"
    )


class AuthConfig:
    def __init__(self, users_db: DataTable, oauth2_scheme: OAuth2PasswordBearer):
        self.users_db = users_db
        self.oauth2_scheme = oauth2_scheme


class UserEntity(Entity):
    def __init__(self, username: str, email: str, full_name: str):
        base = [
            FieldBase("username", FieldTypes.STR, FieldKeyTypes.UNIQUE, username),
            FieldBase("email", FieldTypes.STR, FieldKeyTypes.UNIQUE, email),
            FieldBase("full_name", FieldTypes.STR, FieldKeyTypes.STANDARD, full_name),
            FieldBase("disabled", FieldTypes.BOOL, FieldKeyTypes.STANDARD, False),
            FieldBase("hashed_password", FieldTypes.STR, FieldKeyTypes.STANDARD, ""),
        ]
        entity_fields = []
        for field in base:
            entity_fields.append(EntityField(field))
        super().__init__(entity_fields)
        self.username = username
        self.email = email
        self.full_name = full_name
        self.disabled = False

    @property
    def username(self):
        return self.get_field("username")

    @username.setter
    def username(self, value):
        self.set_field_value("username", value)

    @property
    def email(self):
        return self.get_field("email")

    @email.setter
    def email(self, value):
        self.set_field_value("email", value)

    @property
    def full_name(self):
        return self.get_field("full_name")

    @full_name.setter
    def full_name(self, value):
        self.set_field_value("full_name", value)

    @property
    def disabled(self):
        return self.get_field("disabled")

    @disabled.setter
    def disabled(self, value):
        self.set_field_value("disabled", value)

    @property
    def hashed_password(self):
        return self.get_field("hashed_password")

    @hashed_password.setter
    def hashed_password(self, value):
        self.set_field_value("hashed_password", value)


USER_FIELDS = [
    FieldBase("username", FieldTypes.STR, FieldKeyTypes.UNIQUE, ""),
    FieldBase("email", FieldTypes.STR, FieldKeyTypes.UNIQUE, ""),
    FieldBase("full_name", FieldTypes.STR, FieldKeyTypes.STANDARD, ""),
    FieldBase("disabled", FieldTypes.BOOL, FieldKeyTypes.STANDARD, False),
    FieldBase("hashed_password", FieldTypes.STR, FieldKeyTypes.STANDARD, ""),
]