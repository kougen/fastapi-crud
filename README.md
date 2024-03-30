# FastAPI CRUD with dynamic routers

## Introduction

This is a simple CRUD application using FastAPI. The application uses dynamic routers to create routes for each model in the database.

## Features

- Create, Read, Update, Delete operations for each model
- Dynamic routers for each model
- Custom routes for each model

## Requirements

- Python 3.6+
- FastAPI
- [pyrepositories](https://pypi.org/project/pyrepositories/)

## How to run

First, install the dependencies:

```bash

pip install -r requirements.txt

app = FastAPI()

ds = DataSource(id_type=IdTypes.UUID)

api = CRUDApi(ds, app)

# Registering a router will only setup the route without including it to the app, hence you can add custom endpoints to the router
router = api.register_router("event" , Event).get_base()

# You can add custom routes to the router
@router.get("/test", tags=["event"])
def test():
    return "test"

# You should call this function after all routes are defined to make sure the routes are registered
api.publish()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1112)
```
