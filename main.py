import xpublish
from xpublish import dependencies
from xpublish.routers import base_router, zarr_router
from xpublish_edr.cf_edr_router import cf_edr_router
from xpublish_opendap import dap_router
from xpublish_wms import cf_wms_router
import xarray as xr

import catalog
from settings import settings
from logger import logger






def init_app():
    logger.info(f"Xpublish settings: {settings.dict()}. Loading datasets")

    rest = xpublish.Rest(
        {   key: xr.Dataset()
            for key in catalog.catalog_datasets()
        },
        routers=[
            (base_router, {"tags": ["info"]}),
            (cf_edr_router, {"tags": ["edr"], "prefix": "/edr"}),
            (dap_router, {"tags": ["opendap"], "prefix": "/opendap"}),
            (zarr_router, {"tags": ["zarr"], "prefix": "/zarr"}),
            (cf_wms_router, {"tags": ["wms"], "prefix": "/wms"})
        ],
    )

    app = rest.app

    app.dependency_overrides[dependencies.get_dataset_ids] = catalog.dataset_ids
    app.dependency_overrides[dependencies.get_dataset] = catalog.get_dataset

    edr_description = """
    OGC Environmental Data Retrieval API
    Currently the position query is supported, which takes a single Well Known Text point.

    Requires dataset attributes that can be picked up by cf_xarray, specifically on the
    [axes names or attributes](https://cf-xarray.readthedocs.io/en/latest/coord_axes.html#axis-names)
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
        {"name": "info", "description": "Dataset metadata"},
        {
            "name": "edr",
            "description": edr_description,
            "externalDocs": {
                "description": "OGC EDR Reference",
                "url": "https://ogcapi.ogc.org/edr/",
            },
        },
        {"name": "zarr", "description": zarr_description},
        {"name": "default", "description": "xpublish and environment metadata"},
    ]

    app.title = "xpublish & ERDDAP"
    app.description = """
    Experimenting with xpublish and ERDDAP servers.
    """

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:init_app",
        host=settings.host,
        port=settings.port,
        reload=settings.development,
        log_level=settings.log_level,
        # debug=settings.development,
        proxy_headers=settings.proxied,
        factory=True,
    )
