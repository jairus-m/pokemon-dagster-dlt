import dagster as dg
import dlt
from dlt.sources.rest_api import rest_api_source

@dg.multi_asset(
    outs={
        "pokemon": dg.AssetOut(
            key=[
                "poke_api",
                "pokemon",
            ],  # asset key becomes the table name in target DB
            description="General Pokemon data",
        ),
        "berry": dg.AssetOut(
            key=[
                "poke_api",
                "berry",
            ],  
            description="Berry data which provide HP and status condition restoration, stat enhancement, and even damage negation when eaten by Pokémon",
        ),
        "location": dg.AssetOut(
            key=[
                "poke_api",
                "location",
            ], 
            description="Locations that exist within Pokemon games",
        ),        
    },
    group_name="dltHub__github",
    compute_kind="dlt",
)
def load_pokemon():
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_pokemon",
        destination="duckdb",
        dataset_name="rest_api_data",
    )

    pokemon_source = rest_api_source(
        {
            "client": {
                "base_url": "https://pokeapi.co/api/v2/"
            },
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

    yield dg.Output(value=load_info[0], output_name="pokemon")
    yield dg.Output(value=load_info[1], output_name="berry")
    yield dg.Output(value=load_info[2], output_name="location")
