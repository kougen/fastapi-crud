from click.core import F
from pydantic import BaseModel
from pyrepositories import IdTypes, DataTable, Entity, FieldBase, FieldTypes, FieldKeyTypes
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
