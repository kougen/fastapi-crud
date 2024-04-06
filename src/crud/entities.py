from pydantic import BaseModel
from pyrepositories import Entity, FieldBase, EntityField


class EntityFactory:
    @staticmethod
    def convert_model(model: BaseModel, fields: list[FieldBase]) -> Entity:
        entity_fields = []
        data = model.model_dump()
        for field in fields:
            entity_fields.append(EntityField(field))
        return Entity(entity_fields, id=data.get('id'))

    @staticmethod
    def create_entity(fields: list[FieldBase], data: dict) -> Entity:
        entity_fields = []
        for field in fields:
            value = data.get(field.name)
            entity_fields.append(EntityField(field, value))
        return Entity(entity_fields)
