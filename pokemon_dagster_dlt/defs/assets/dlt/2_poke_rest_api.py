"""
This example demonstrates the use of the official dlt-Dagster integration (`dagster-dlt`)
to materialize multiple assets from three endpoints of the PokeAPI REST API.

Key features:
- Leverages the @dlt_assets decorator to automatically generate Dagster assets from a dlt source and pipeline.
- Uses a custom DagsterDltTranslator to control asset key naming and dependencies.
- Data from the 'pokemon', 'berry', and 'location' endpoints is loaded into a DuckDB database.
- The integration enables seamless orchestration, monitoring, and management of dlt pipelines within Dagster.

References:
- Dagster dlt integration docs: https://docs.dagster.io/integrations/libraries/dlt
- dltHub REST API source tutorial: https://dlthub.com/docs/tutorial/rest-api

Note: Adding extra comments for instruction/demo purposes.
"""

import dagster as dg
import dlt
from dlt.extract.resource import DltResource
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dlt.sources.rest_api import rest_api_source
from collections.abc import Iterable

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

    - get_asset_key: Prefixes each asset key with 'poke_api_2' for better organization in the Dagster UI.
    - get_deps_asset_keys: Specifies that assets have no upstream dependencies (flat structure).
    """
    def get_asset_key(self, resource: DltResource) -> dg.AssetKey:
        """Asset key is the resource name, prefixed with 'poke_api_2'"""
        return dg.AssetKey(f"{resource.name}").with_prefix("poke_api_2")

    def get_deps_asset_keys(self, resource: DltResource) -> Iterable[dg.AssetKey]:
        """No upstream dependencies for these assets"""
        return []

@dlt_assets(
    dlt_source=pokemon_source,
    dlt_pipeline=dlt.pipeline(
        pipeline_name="rest_api_pokemon_2",  # Output .duckdb file will be named after this pipeline
        dataset_name="poke_rest_api_2",      # Logical dataset name within DuckDB
        destination="duckdb",
    ),
    group_name="dltHub__poke_2",             # Asset group name in Dagster UI
    dagster_dlt_translator=CustomDagsterDltTranslator(),  # Use custom asset key translation
)
def load_pokemon_2(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    """
    Materializes assets by running the dlt pipeline within Dagster's orchestration context.
    Args:
        context (AssetExecutionContext): Dagster context for asset execution.
        dlt (DagsterDltResource): Resource providing access to dlt pipeline execution.
    Yields:
        Materialization results for each dlt resource (pokemon, berry, location) as Dagster assets.
    """
    # Trigger the dlt pipeline run and yield materialized asset results for Dagster.
    yield from dlt.run(context=context)
