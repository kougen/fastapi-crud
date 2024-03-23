from typing import List
from enum import Enum
from fastapi import Depends, FastAPI
from pyrepositories import DataSource, Entity
from pydantic import create_model
from fastapi.routing import APIRouter
from .entities import EntityFactory

id_path = '/single/{id}'

def construct_path(base_path: str, path: str, is_plural: bool, use_prefix: bool) -> str:
    plural = 's' if is_plural else ''
    if not use_prefix:
        return f'{base_path}{plural}{path}'
    else:
        return f'{path}'
    

def get_tags(name: str, use_name_as_tag: bool) -> List[str | Enum] | None:
    return [name] if use_name_as_tag else []


def get_prefix(name: str, use_prefix: bool) -> str:
    return f'/{name}' if use_prefix else ''


def format_entities(entities: List[Entity]) -> List[dict]:
    return [entity.serialize() for entity in entities]

class CRUDApiRouter:
    def __init__(self, datasource: DataSource, name: str, model_type: type, factory: EntityFactory, use_prefix: bool = True, use_name_as_tag: bool = True):
        self.datasource = datasource
        self.name = name
        self.use_prefix = use_prefix
        self.use_name_as_tag = use_name_as_tag
        datatype = name.lower()
        tags = get_tags(name, use_name_as_tag)
        table = self.datasource.get_table(datatype)
        if not table:
            raise ValueError(f'Table {datatype} not found in datasource')

        filters = table.get_filter_fields()
        base_path = f'/{datatype}'

        self.router = APIRouter(
            prefix=get_prefix(datatype, use_prefix)
        )

        @self.router.get(construct_path(f'{base_path}', '', True, use_prefix), tags=tags)
        async def read_items():
            return format_entities(self.datasource.get_all(datatype) or [])

        @self.router.get(construct_path(f'{base_path}', '/filter', True, use_prefix), tags=tags)
        async def filter_items(params: create_model("Query", **filters) = Depends()):
            fields = params.dict()
            return format_entities(self.datasource.get_by_filter(datatype, fields) or [])

        @self.router.get(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def read_item(id: int | str):
            return self.datasource.get_by_id(datatype, id)

        @self.router.post(construct_path(base_path, '', False, use_prefix), tags=tags)
        async def create_item(item: model_type):
            return self.datasource.insert(datatype, factory.create_entity(item.model_dump()))

        @self.router.put(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def update_item(id: int | str, item: model_type):
            entity = factory.create_entity(item.model_dump())
            return self.datasource.update(datatype, id, entity)

        @self.router.delete(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def delete_item(id: int | str):
            return self.datasource.delete(datatype, id)

        @self.router.delete(construct_path(base_path, '', True, use_prefix), tags=tags)
        async def delete_all_items():
            return self.datasource.clear(datatype)

    def get_router(self):
        return self.router


class CRUDApi:
    def __init__(self, datasource: DataSource, app: FastAPI):
        self.datasource = datasource
        self.app = app
        self.routers = [] # List[CRUDApiRouter]


    def add_router(self, datatype: str, model_type: type, factory: EntityFactory = EntityFactory(), use_prefix: bool = True):
        router = CRUDApiRouter(self.datasource, datatype, model_type, factory, use_prefix)
        self.routers.append(router)
        self.app.include_router(router.get_router())

        



