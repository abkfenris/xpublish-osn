import xpublish
from xpublish import dependencies as x_dep
from xpublish.routers import base_router, zarr_router
from xpublish_edr.cf_edr_router import cf_edr_router

from dependencies import (
    datasets_for_server,
    get_datasets,
    dataset_ids,
    get_dataset,
    get_some_datasets,
)
from settings import settings

rest = xpublish.Rest(
    get_some_datasets(),
    routers=[
        (base_router, {"tags": ["info"]}),
        (cf_edr_router, {"tags": ["edr"], "prefix": "/edr"}),
        (zarr_router, {"tags": ["zarr"], "prefix": "/zarr"}),
    ],
)

app = rest.app

app.dependency_overrides[x_dep.get_dataset_ids] = dataset_ids
app.dependency_overrides[x_dep.get_dataset] = get_dataset

edr_description = """
OGC Environmental Data Retrieval API
Currently the position query is supported, which takes a single Well Known Text point.
"""


zarr_description = """
Zarr access to NetCDF datasets.
Load by using an fsspec mapper
```python
mapper = fsspec.get_mapper("/datasets/{dataset_id}/zarr/")
ds = xr.open_zarr(mapper, consolidated=True)
```
"""

app.openapi_tags = [
    {"name": "info"},
    {
        "name": "edr",
        "description": edr_description,
        "externalDocs": {
            "description": "OGC EDR Reference",
            "url": "https://ogcapi.ogc.org/edr/",
        },
    },
    {"name": "zarr", "description": zarr_description},
]

if __name__ == "__main__":
    import uvicorn

    print(settings)

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.development,
        log_level=settings.log_level,
        debug=settings.development,
        proxy_headers=settings.proxied,
    )
