"""
This example uses the dagster-dlt library within the Dagster framework (official integration) to materialize
multi-assets from 3 endpoints of a single REST API source.
"""

import dagster as dg
import dlt
from dlt.extract.resource import DltResource
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dlt.sources.rest_api import rest_api_source
from collections.abc import Iterable

pokemon_source = rest_api_source(
    {
        "client": {"base_url": "https://pokeapi.co/api/v2/"},
        "resource_defaults": {
            "endpoint": {
                "params": {
                    "limit": 1000,
                },
            },
        },
        "resources": [
            "pokemon",
            "berry",
            "location",
        ],
    }
)

class CustomDagsterDltTranslator(DagsterDltTranslator):
     def get_asset_key(self, resource: DltResource) -> dg.AssetKey:
         """Overrides asset key to be the dlt resource name with a 'pokemon' prefix."""
         return dg.AssetKey(f"{resource.name}").with_prefix("poke_api_2")

     def get_deps_asset_keys(self, resource: DltResource) -> Iterable[dg.AssetKey]:
         """Overrides upstream asset key to be a single source asset."""
         return []

@dlt_assets(
    dlt_source=pokemon_source,
    dlt_pipeline=dlt.pipeline(
        pipeline_name="rest_api_pokemon_2", # .duckdb file named after pipeline
        dataset_name="poke_rest_api_2",
        destination="duckdb",
    ),
    group_name="dltHub__poke_2",
    dagster_dlt_translator=CustomDagsterDltTranslator(),
)

def load_pokemon_2(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)
