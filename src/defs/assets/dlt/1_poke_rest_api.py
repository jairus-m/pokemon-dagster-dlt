"""
This module demonstrates how to use the dlt library within the Dagster framework (without the official integration)
to materialize multiple assets from three different endpoints of the PokeAPI REST API.

The example is adapted from dltHub's REST API Source tutorial:
https://dlthub.com/docs/tutorial/rest-api

Core approach:
- Uses Dagster's @multi_asset decorator to define a single asset function that materializes three distinct assets
  (pokemon, berry, location) from a single dlt pipeline run.
- Each asset corresponds to a specific endpoint/resource in the PokeAPI.
- Asset metadata (keys, descriptions) is configured for visibility in the Dagster UI.
- Data is loaded into a DuckDB database using dlt.

Architecture: 
- Lightweight Dagster wrapper around dlt's REST API source
Control Level: 
- Medium (pipeline config exposed, resources hidden)
  - dlt: EL is heavily declarative
  - Dagster: Metadata/Dependencies are explicitly configured

Note: 
  - Adding extra comments for instruction/demo purposes.
  - The `.duckdb` file will be created in the current working directory as `rest_api_pokemon_1.duckdb`
"""

import dagster as dg
import dlt
from dlt.sources.rest_api import rest_api_source
from src.defs.utils import DUCKDB_PATH # could be an environment variable or config parameter

@dg.multi_asset(
    outs={  # Define Dagster asset definitions/metadata for the 3 dlt Assets
        "pokemon": dg.AssetOut(
            key=[
                "poke_api_1", # Asset key prefix
                "pokemon_1",  # Asset key name
            ],
            description="General Pokemon data retrieved from the PokeAPI /pokemon endpoint.", # Asset description
        ),
        "berry": dg.AssetOut(
            key=[
                "poke_api_1",
                "berry_1",
            ],
            description=(
                "Berry characteristics from /berry endpoint including growth time, size, "
                "and cultivation properties. Affects Pokemon stats when consumed."
            ),
        ),
        "location": dg.AssetOut(
            key=[
                "poke_api_1",
                "location_1",
            ],
            description="In-game locations from /location endpoint with regional data and game appearances",
        ),
    },
    group_name="dltHub__poke_1",  # Asset group name in Dagster UI
    compute_kind="dlt",
)
def load_pokemon_1():
    """
    Loads data from three endpoints of the PokeAPI using dlt and materializes them as separate Dagster assets.

    Steps:
    1. Initializes a dlt pipeline that targets a DuckDB database. The pipeline name determines the output .duckdb file.
    2. Configures a dlt REST API source to pull data from the /pokemon, /berry, and /location endpoints with a high limit.
    3. Runs the pipeline (which fetches and loads the data into the DuckDB destination).
    4. Returns a separate Dagster Output for each resource, matching the order of the resources in the source config.

    Returns:
        Tuple[Output, Output, Output]: Dagster Output objects for pokemon, berry, and location assets, respectively.
    """

    # Initialize the dlt pipeline with DuckDB as the destination.
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_pokemon_1",
        destination=dlt.destinations.duckdb(DUCKDB_PATH + "rest_api_pokemon_1.duckdb"),  # Path to the DuckDB database file
        dataset_name="poke_rest_api_1",      # Logical dataset name within the DuckDB database
    )

    # Define the REST API source configuration for dlt.
    # - base_url: Root URL for the PokeAPI
    # - resource_defaults: Default query parameters (e.g., limit=1000 for all endpoints)
    # - resources: List of endpoint names to fetch
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
                "pokemon",   # /pokemon endpoint
                "berry",     # /berry endpoint
                "location",  # /location endpoint
            ],
        }
    )

    # Run the pipeline, which loads data from all specified resources into DuckDB.
    # The returned load_info is a list of load result objects, one per resource (order matches the 'resources' list).
    load_info = pipeline.run(pokemon_source)
    print(load_info)  # For debugging/inspection in local runs

    # Dagster expects either yielded outputs or a tuple of Output objects when multiple outputs are defined.
    # Here, we return the load_info for each resource as separate Dagster Outputs, in the same order as the outs dict.
    return (
        dg.Output(value=load_info[0]),  # Output for the 'pokemon' asset
        dg.Output(value=load_info[1]),  # Output for the 'berry' asset
        dg.Output(value=load_info[2]),  # Output for the 'location' asset
    )
