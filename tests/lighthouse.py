import os
import sys
from pathlib import Path
from fastapi import FastAPI, Query
import uvicorn
from typing import Annotated



path_root = Path(__file__).parents[1]
sys.path.append(os.path.join(path_root, 'src'))

from fastapi_bootstrap import CRUDApi, DataSource, DataTable, FilterField

app = FastAPI()

t = DataTable("event")
t.set_filter_fields({
    "name": (str, "My Name"),
    "date": (str,),
    "location": (str,),
    "description": (str,)
})
t.add_filter_field(FilterField("ids", Annotated[list[str], Query()]))
ds = DataSource([t])

api = CRUDApi(ds, app)

api.add_router("event")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1111)


