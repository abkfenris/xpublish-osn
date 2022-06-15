from fastapi import Depends, Path
import httpx
import xarray as xr
import cf_xarray as cfxr
from xpublish.dependencies import get_cache
from xpublish.utils.cache import CostTimer

from settings import settings

xr.set_options(keep_attrs=True)


headers = {"user-agent": settings.user_agent, "accept": "application/json"}


def reshape_dataset_response(table: dict) -> dict[str, str]:
    """ Returns the dataset ID and ERDDAP urls for datasets """
    griddap_url_index = table["columnNames"].index("griddap")
    dataset_id = table["columnNames"].index("Dataset ID")

    datasets = {row[dataset_id]: row[griddap_url_index] for row in table["rows"]}

    return datasets


def griddap_info_url(server_base_url: str) -> str:
    """ Returns the info.json URL for the griddap datasets """
    server_base = server_base_url.rstrip("/")
    return f"{server_base}/griddap/index.json"


async def datasets_for_server(server_base_url: str) -> dict[str, str]:
    """ Returns the dataset IDs and URLS for given ERDDAP server"""
    url = griddap_info_url(server_base_url)

    async with httpx.AsyncClient(headers=headers) as client:
        r = await client.get(url, follow_redirects=True)

    data = r.json()["table"]

    return reshape_dataset_response(data)


def get_some_datasets():
    """ Get just enough datasets to initialize things since an empty dict evaluates to false """
    datasets = {}

    with httpx.Client(headers=headers) as client:
        for server_id, server_url in settings.erddap_servers.items():
            griddap_url = griddap_info_url(server_url)
            r = client.get(griddap_url, follow_redirects=True)

            table = r.json()["table"]

            server_datasets = reshape_dataset_response(table)

            for dataset_id, dataset_url in server_datasets.items():
                datasets[f"{server_id}-{dataset_id}"] = xr.open_dataset(dataset_url)

                if len(datasets) > 1:
                    return datasets


async def get_datasets(cache=Depends(get_cache)):
    """ Returns all dataset IDs and URLs for all ERDDAP servers """
    cache_key = "get_datasets"
    datasets = cache.get(cache_key, {})

    if not datasets:
        with CostTimer() as ct:
            for server_id, server_url in settings.erddap_servers.items():
                server_datasets = await datasets_for_server(server_url)

                for dataset_id, dataset_url in server_datasets.items():
                    datasets[f"{server_id}-{dataset_id}"] = dataset_url

        cache.put(cache_key, datasets, ct.time)

    return datasets


def dataset_ids(datasets=Depends(get_datasets)):
    """ Just the dataset IDs """
    return list(datasets)


def get_dataset(
    server_dataset_id: str = Path(..., alias="dataset_id"), cache=Depends(get_cache)
) -> xr:
    """ Get an xarray dataset based on dataset_id in URL """
    ds = cache.get(server_dataset_id)

    if ds is None:
        with CostTimer() as ct:
            server_id, dataset_id = server_dataset_id.split("-", maxsplit=1)

            server_url = settings.erddap_servers[server_id]

            dataset_url = f"{server_url.rstrip('/')}/griddap/{dataset_id}"

            dataset = xr.open_dataset(dataset_url)
            dataset.attrs["erddap_url"] = dataset_url

        cache.put(server_dataset_id, ds, ct.time)

    return dataset
