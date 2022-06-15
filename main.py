import xpublish
from xpublish import dependencies as x_dep
from xpublish.routers import base_router, zarr_router
from xpublish_edr.cf_edr_router import cf_edr_router

from dependencies import dataset_ids, get_dataset, get_some_datasets
from settings import settings
from logger import logger


def init_app():
    logger.info(f"Xpublish settings: {settings.dict()}")

    initial_datasets = get_some_datasets()

    rest = xpublish.Rest(
        initial_datasets,
        routers=[
            (base_router, {"tags": ["info"]}),
            (cf_edr_router, {"tags": ["edr"], "prefix": "/edr"}),
            (zarr_router, {"tags": ["zarr"], "prefix": "/zarr"}),
        ],
    )

    app = rest.app

    app.dependency_overrides[x_dep.get_dataset_ids] = dataset_ids
    app.dependency_overrides[x_dep.get_dataset] = get_dataset

    if settings.sentry_dsn:
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

        app.add_middleware(SentryAsgiMiddleware)

    @app.get("/servers")
    def erddap_servers():
        """ 
        ERDDAP server IDs and URLs 

        `/dataset/{dataset_id}/` in paths are constructed of `{server_id}-{erddap_dataset_id}`
        """
        return settings.erddap_servers

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
        debug=settings.development,
        proxy_headers=settings.proxied,
        factory=True,
    )
