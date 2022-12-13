import intake
from fastapi import Depends, Path
import xarray as xr
from xpublish.dependencies import get_cache
from xpublish.utils.cache import CostTimer

url = 'https://mghp.osn.xsede.org/rsignellbucket1/catalogs/ioos_intake_catalog.yml'
cat = intake.open_catalog(url)

def catalog_datasets():
    datasets = {}

    for key in cat:
        datasets[key] = cat[key].description

    return datasets


def dataset_ids(datasets=Depends(catalog_datasets)):
    return list(datasets)


def get_dataset(dataset_id: str = Path(...), cache=Depends(get_cache)) -> xr.Dataset:
    ds = cache.get(dataset_id)

    if ds is None:
        with CostTimer() as ct:
            ds = cat[dataset_id].to_dask()
        
        cache.put(dataset_id, ds, ct.time)
    
    return ds
