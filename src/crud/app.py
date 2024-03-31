from typing import Annotated, List
from enum import Enum
from fastapi import Depends, FastAPI
from pyrepositories import DataSource, Entity, FieldBase, FieldTypes
from fastapi import Depends, FastAPI, HTTPException, status
from pyrepositories import DataSource, Entity
from pydantic import create_model
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .entities import EntityFactory
from .lib import convert_field_to_filter, convert_dict_to_filter
from .lib import AuthConfig, decode_token, User

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


def convert2int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


class CRUDApiRouter:
    def __init__(
            self, 
            datasource: DataSource, 
            name: str, 
            model_type: type, 
            factory: EntityFactory, 
            use_prefix: bool = True, 
            use_name_as_tag: bool = True,
            auth: AuthConfig | None = None
        ):
        self.__datasource = datasource
        self.__is_included = False
        self.__auth = auth
        self.name = name
        self.use_prefix = use_prefix
        self.use_name_as_tag = use_name_as_tag
        datatype = name.lower()
        tags = get_tags(name, use_name_as_tag)
        self.__table = self.__datasource.get_table(datatype)
        if not self.__table:
            raise ValueError(f'Table {datatype} not found in datasource')

        base_path = f'/{datatype}'

        self.__router = APIRouter(
            prefix=get_prefix(datatype, use_prefix)
        )

        if auth:
            self.__setup_routes_with_auth(base_path, tags, datatype, model_type, factory, use_prefix)
        else:
            self.__setup_routes(base_path, tags, datatype, model_type, factory, use_prefix)


    def get_base(self):
        return self.__router

    def get_datasource(self):
        return self.__datasource

    @property
    def is_included(self):
        return self.__is_included

    def include(self):
        self.__is_included = True

    def __setup_routes_with_auth(self, base_path: str, tags: List[str | Enum] | None, datatype: str, model_type: type, factory: EntityFactory, use_prefix: bool):
        if not self.__table:
            raise ValueError(f'Table {datatype} not found in datasource')
        filters = self.__table.get_filter_fields()
        @self.__router.get(construct_path(f'{base_path}', '', True, use_prefix), tags=tags)
        async def read_items(token: Annotated[str, Depends(self.__auth)]):
            return format_entities(self.__datasource.get_all(datatype) or [])

        @self.__router.get(construct_path(f'{base_path}', '/filter', True, use_prefix), tags=tags)
        async def filter_items(token: Annotated[str, Depends(self.__auth)], params: create_model("Query", **filters) = Depends()):
            fields = params.dict()
            return format_entities(self.__datasource.get_by_filter(datatype, fields) or [])

        @self.__router.get(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def read_item(token: Annotated[str, Depends(self.__auth)], id: int | str):
            return self.__datasource.get_by_id(datatype, id)

        @self.__router.post(construct_path(base_path, '', False, use_prefix), tags=tags)
        async def create_item(token: Annotated[str, Depends(self.__auth)], item: model_type):
            return self.__datasource.insert(datatype, factory.create_entity(item.model_dump()))

        @self.__router.put(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def update_item(token: Annotated[str, Depends(self.__auth)], id: int | str, item: model_type):
            entity = factory.create_entity(item.model_dump())
            if isinstance(id, str) and convert2int(id):
                id = int(id)
            return self.__datasource.update(datatype, id, entity)

        @self.__router.delete(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def delete_item(token: Annotated[str, Depends(self.__auth)], id: int | str):
            if isinstance(id, str) and convert2int(id):
                id = int(id)
            return self.__datasource.delete(datatype, id)

        @self.__router.delete(construct_path(base_path, '', True, use_prefix), tags=tags)
        async def delete_all_items(token: Annotated[str, Depends(self.__auth)]):
            return self.__datasource.clear(datatype)

    def __setup_routes(self, base_path: str, tags: List[str | Enum] | None, datatype: str, model_type: type, factory: EntityFactory, use_prefix: bool):
        if not self.__table:
            raise ValueError(f'Table {datatype} not found in datasource')
        filters = self.__table.get_filter_fields()
        @self.__router.get(construct_path(f'{base_path}', '', True, use_prefix), tags=tags)
        async def read_items():
            return format_entities(self.__datasource.get_all(datatype) or [])
        
        if len(filters) > 0:
            filter_dict = convert_field_to_filter(filters)

            @self.__router.get(construct_path(f'{base_path}', '/filter', True, use_prefix), tags=tags)
            async def filter_items(params: create_model("Query", **filter_dict) = Depends()):
                fields = params.dict()
                processed_filters = convert_dict_to_filter(fields)
                result = format_entities(self.__datasource.get_by_filter(datatype, processed_filters) or [])
                return result

        @self.__router.get(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def read_item(id: int | str):
            return self.__datasource.get_by_id(datatype, id)

        @self.__router.post(construct_path(base_path, '', False, use_prefix), tags=tags)
        async def create_item(item: model_type):
            try:
                entity = factory.create_entity(table.field_structure, item.model_dump())
                result = self.__datasource.insert(datatype, entity)
                if result:
                    return {'success': True, 'created_entity': result.serialize()}
                else:
                    return {'success': False}
            except Exception as e:
                return {'success': False, 'error': str(e)}

        @self.__router.put(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def update_item(item_id: int | str, item: model_type):
            try:
                entity = factory.create_entity(table.field_structure, item.model_dump())
                if isinstance(item_id, str) and convert2int(item_id):
                    item_id = int(item_id)
                result = self.__datasource.update(datatype, item_id, entity)
                if result:
                    return {'success': True, 'updated_entity': result.serialize()}
                return {'success': False}
            except Exception as e:
                return {'success': False, 'error': str(e)}

        @self.__router.delete(construct_path(base_path, id_path, False, use_prefix), tags=tags)
        async def delete_item(item_id: int | str):
            try:
                if isinstance(item_id, str) and convert2int(item_id):
                    item_id = int(item_id)
                result = self.__datasource.delete(datatype, item_id)
                if result:
                    return {'success': True, 'deleted_id': item_id}
                return {'success': False}
            except Exception as e:
                return {'success': False, 'error': str(e)}

        @self.__router.delete(construct_path(base_path, '', True, use_prefix), tags=tags)
        async def delete_all_items():
            return self.__datasource.clear(datatype)


class CRUDApi:
    def __init__(self, datasource: DataSource, app: FastAPI, auth: AuthConfig | None = None):
        self.__datasource = datasource
        self.__app = app # type: FastAPI
        self.__routers = {} # type: dict[str, CRUDApiRouter]
        self.__auth = auth

        if self.__auth:
            self.__setup_auth()

    def __setup_auth(self):
        if not self.__auth:
            return None

        globalAuth = self.__auth

        def get_user(username: str):
            return globalAuth.users_db.get_by_filter({"username": username})


        def fake_decode_token(token: str):
            # This doesn't provide any security at all
            # Check the next version
            user = get_user(token)
            return user

        async def get_current_user(token: Annotated[str, Depends(self.__auth.oauth2_scheme)]):
            user = fake_decode_token(token)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user


        async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
            if current_user.disabled:
                raise HTTPException(status_code=400, detail="Inactive user")
            return current_user


        def fake_hash_password(password: str):
            return "fakehashed" + password


        @self.__app.post("/token", tags=["auth"])
        async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
            results = globalAuth.users_db.get_by_filter({"username": form_data.username})
            if len(results) != 1:
                raise HTTPException(status_code=400, detail="Incorrect username or password")
            user = results[0]
            hashed_password = fake_hash_password(form_data.password)
            if not hashed_password == user.hashed_password:
                raise HTTPException(status_code=400, detail="Incorrect username or password")

            return {"access_token": user.username, "token_type": "bearer"}


        @self.__app.get("/users/me", tags=["auth"])
        async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
            return current_user

    def get_app(self) -> FastAPI:
        return self.__app

    def get_routers(self):
        return self.__routers

    def get_router(self, datatype: str) -> CRUDApiRouter | None:
        return self.__routers.get(datatype)

    def get_datasource(self) -> DataSource:
        return self.__datasource

    def register_router(self, datatype: str, model_type: type, factory: EntityFactory = EntityFactory(), use_prefix: bool = True, filters: list[FieldBase] = []) -> CRUDApiRouter:
        router = CRUDApiRouter(self.__datasource, datatype, model_type, factory, use_prefix, filters=filters)
        self.__routers[datatype] = router
        return router

    def include_router(self, datatype: str, model_type: type, factory: EntityFactory = EntityFactory(), use_prefix: bool = True, filters: list[FieldBase] = []) -> CRUDApiRouter:
        router = self.register_router(datatype, model_type, factory, use_prefix, filters)
        self.__app.include_router(router.get_base())
        router.include()
        return router

    def publish(self):
        for router in self.__routers.values():
            if not router.is_included:
                self.__app.include_router(router.get_base())
