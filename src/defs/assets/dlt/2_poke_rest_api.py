"""
This file demonstrates the use of the official dlt-Dagster integration (`dagster-dlt`)
to materialize multiple assets from three endpoints of the PokeAPI REST API.

Core approach:
- Fully declarative and integrated approach
- Leverages the @dg.dlt_assets decorator to automatically generate Dagster assets from a dlt source and pipeline.
- Need to use a custom DagsterDltTranslator class to control asset key naming and dependencies.
- The integration enables streamlined orchestration, monitoring, and management of dlt pipelines within Dagster.
- Data from the 'pokemon', 'berry', and 'location' endpoints is loaded into a DuckDB database.

Architecture: 
- Coupled code integration via dagster-dlt
Control Level: 
- Low (convention over configuration)
  - dlt: EL is heavily declarative
  - Dagster:
    - Metadata: Auto-generated from dlt schema
    - Dependencies are inferred from source

References:
- Dagster dlt integration docs: https://docs.dagster.io/integrations/libraries/dlt
- dltHub REST API source tutorial: https://dlthub.com/docs/tutorial/rest-api

Note: 
  - Adding extra comments for instruction/demo purposes.
  - The `.duckdb` file will be created in the current working directory as `rest_api_pokemon_2.duckdb`
"""

import dagster as dg
import dlt
from dlt.extract.resource import DltResource
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dagster_dlt.translator import DltResourceTranslatorData
from dlt.sources.rest_api import rest_api_source
from collections.abc import Iterable
from src.defs.utils import DUCKDB_PATH # could be an environment variable or config parameter

# Define the dlt source for the PokeAPI.
# This configuration specifies the base URL, default parameters (limit=1000), and the resources to extract.
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
            "pokemon",   # General Pokemon data
            "berry",     # Berry data
            "location",  # Location data
        ],
    }
)

class CustomDagsterDltTranslator(DagsterDltTranslator):
    """
    Custom translator to control how dlt resources are mapped to Dagster asset keys and dependencies.
    Unlike the other examples that configured these core asset attributes within the `@dg.multi_asset`
    decorator, custom metadata/dependecies have to be configured here. 

    - get_asset_key: Prefixes each asset key with 'poke_api_2' for better organization in the Dagster UI.
    - get_deps_asset_keys: Specifies that assets have no upstream dependencies (flat structure).
    - get_asset_spec: Returns a representation of an asset as an AssetSpec object (contains the core attributes of the asset)
    """
    def get_asset_key(self, resource: DltResource) -> dg.AssetKey:
        """Asset key is the resource name, prefixed with 'poke_api_2'"""
        return dg.AssetKey(f"{resource.name}_2").with_prefix("poke_api_2")

    def get_deps_asset_keys(self, resource: DltResource) -> Iterable[dg.AssetKey]:
        """No upstream dependencies for these assets"""
        return []
    
    def get_asset_spec(self, data: DltResourceTranslatorData) -> dg.AssetSpec:
        """Maps asset descriptions"""
        default_spec = super().get_asset_spec(data)
        asset_key_str = "/".join(default_spec.key.path) # Create string of asset keys that match `dg list defs`
        # Set custom descriptions based on the asset key
        descriptions = {
            "poke_api_2/location_2": "In-game locations from /location endpoint with regional data and game appearances",
            "poke_api_2/berry_2": "Berry characteristics from /berry endpoint including growth time, size and cultivation properties. Affects Pokemon stats when consumed.", 
            "poke_api_2/pokemon_2": "General Pokemon data retrieved from the PokeAPI /pokemon endpoint.",
        }
        description = descriptions.get(asset_key_str, "Default description")
        return default_spec.replace_attributes(description=description) # Map the proper description

@dlt_assets(
    dlt_source=pokemon_source,
    dlt_pipeline=dlt.pipeline(
        pipeline_name="rest_api_pokemon_2",  
        dataset_name="poke_rest_api_2",      # Logical dataset name within DuckDB
        destination=dlt.destinations.duckdb(DUCKDB_PATH + "rest_api_pokemon_2.duckdb"),
    ),
    group_name="dltHub__poke_2",             # Asset group name in Dagster UI
    dagster_dlt_translator=CustomDagsterDltTranslator(),  # Use custom asset key translation
)
def load_pokemon_2(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    """
    Materializes assets by running the dlt pipeline within Dagster's orchestration context.
    Note:
        Because multi asset metadata is inferred with the dlt-dagster library and not easily configured 
        for each individual asset, the asset descriptions will inherit this docstring of the @dlt_asset decorated function load_pokemon_2 
        for each asset. If this docstring was blank, there would be no description populated. 
    Args:
        context (AssetExecutionContext): Dagster context for asset execution.
        dlt (DagsterDltResource): Resource providing access to dlt pipeline execution.
    Yields:
        Materialization results for each dlt resource (pokemon, berry, location) as Dagster assets.
    """
    # Trigger the dlt pipeline run and yield materialized asset results for Dagster.
    yield from dlt.run(context=context)
