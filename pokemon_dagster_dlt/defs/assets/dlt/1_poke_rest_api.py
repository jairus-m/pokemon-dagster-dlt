"""
This example uses the dlt library within the Dagster framework (non-integration) to materialize
multi-assets from 3 endpoints of a single REST API source.

The dltHub example is pulled directly from: https://dlthub.com/docs/tutorial/rest-api.
  - The dltHub code is simply wrapped with the @dg.multi_asset decorator
"""

import dagster as dg
import dlt
from dlt.sources.rest_api import rest_api_source


@dg.multi_asset(
    outs={
        "pokemon": dg.AssetOut(
            key=[ # asset key becomes the table name in target DB
                "poke_api_1",
                "pokemon_1",
            ],  
            description="General Pokemon data", # description associated with asset, viewable in Dagster UI
        ),
        "berry": dg.AssetOut(
            key=[
                "poke_api_1",
                "berry_1",
            ],
            description="Berry data which provide HP and status condition restoration, stat enhancement, and even damage negation when eaten by Pokémon",
        ),
        "location": dg.AssetOut(
            key=[
                "poke_api_1",
                "location_1",
            ],
            description="Locations that exist within Pokemon games",
        ),
    },
    group_name="dltHub__poke_1",
    compute_kind="dlt",
)
def load_pokemon_1():
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_pokemon",
        destination="duckdb",
        dataset_name="poke_rest_api_1",
    )

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

    load_info = pipeline.run(pokemon_source)
    print(load_info)

    # when an op is defined to have multiple outputs, Dagster expects the function
    # to either yield each output individually or return a tuple containing a value for each output
    return (
        dg.Output(value=load_info[0]), # returning dlt load_info object corresponding to each resource (pokemon)
        dg.Output(value=load_info[1]), # berry
        dg.Output(value=load_info[2]), # location
    )
