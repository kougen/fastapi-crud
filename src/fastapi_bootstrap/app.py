from typing import List
from enum import Enum
from fastapi import Depends, FastAPI
from pydantic import create_model, BaseModel
from fastapi.routing import APIRouter
from .datasource import DataSource

id_path = '/{id}'

def construct_path(base_path: str, path: str, is_plural: bool, use_prefix: bool) -> str:
    plural = 's' if is_plural else ''
    if not use_prefix:
        return f'{base_path}{plural}{path}'
    else:
        return f'{plural}{path}'
    

def get_tags(name: str, use_name_as_tag: bool) -> List[str | Enum] | None:
    return [name] if use_name_as_tag else []


def get_prefix(name: str, use_prefix: bool) -> str:
    return f'/{name}' if use_prefix else ''

class CRUDApiRouter:
    def __init__(self, datasource: DataSource, name: str, use_prefix: bool = True, use_name_as_tag: bool = True):
        self.datasource = datasource
        self.name = name
        self.use_prefix = use_prefix
        self.use_name_as_tag = use_name_as_tag
        datatype = name.lower()
        tags = get_tags(name, use_name_as_tag)
        table = self.datasource.get_table(datatype)
        base_path = f'/{datatype}'


        self.router = APIRouter(
            prefix=get_prefix(datatype, use_prefix)
        )

        if not table:
            return

        @self.router.get(construct_path(f'{base_path}', '', True, use_prefix), tags=tags)
        async def read_items():
            return self.datasource.get_all(datatype)

        @self.router.get(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def read_item(id: int):
            return self.datasource.get_by_id(datatype, id)
        filters = table.get_filter_fields()

        @self.router.get(construct_path(f'{base_path}', '/filter', True, use_prefix), tags=tags)
        async def read_filtered_items(params: create_model("Query", **filters) = Depends()):
            params_as_dict = params.dict()
            return self.datasource.get_by_filter(datatype, params_as_dict)

        @self.router.post(construct_path(base_path, '', False, use_prefix), tags=tags)
        async def create_item(item: dict):
            return self.datasource.insert(datatype, item)

        @self.router.put(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def update_item(id: int, item: dict):
            return self.datasource.update(datatype, id, item)

        @self.router.delete(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def delete_item(id: int):
            return self.datasource.delete(datatype, id)

    def get_router(self):
        return self.router


class CRUDApi:
    def __init__(self, datasource: DataSource, app: FastAPI):
        self.datasource = datasource
        self.app = app
        self.routers = [] # List[CRUDApiRouter]


    def add_router(self, datatype: str, use_prefix: bool = True):
        router = CRUDApiRouter(self.datasource, datatype, use_prefix)
        self.routers.append(router)
        self.app.include_router(router.get_router())

        



