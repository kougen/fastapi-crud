from pydantic import BaseModel
from pyrepositories import Entity


class EntityFactory:
    def convert_model(self, model: BaseModel) -> Entity:
        fields = model.model_dump()
        if 'id' in fields:
            entity = Entity(id=fields['id'])
            entity.fields = fields
        print("Override this method to create an entity")
        return Entity()

    def create_entity(self, fields: dict) -> Entity:
        entity = Entity(fields.get('id'))
        entity.fields = fields
        return entity
