import dagster as dg
import dlt
import requests
@dlt.resource
def pokemon_resource():
    """
    A dlt resource to extract data from the Pokemon REST API.
    This function fetches data from the Pokemon endpoint and yields the response.
    Args:
        None
    Yields:
        Generator: Yields the response object from the Pokemon REST API.
    """
    url = "https://pokeapi.co/api/v2/pokemon"
    response = requests.get(url)
    response.raise_for_status()
    yield response.json()
@dlt.resource
def berry_resource():
    """
    A dlt resource to extract data from the Pokemon REST API.
    This function fetches data from the Berry endpoint and yields the response.
    Args:
        None
    Yields:
        Generator: Yields the response object from the Pokemon REST API.
    """
    url = "https://pokeapi.co/api/v2/berry"
    response = requests.get(url)
    response.raise_for_status()
    yield response.json()
@dlt.resource
def location_resource():
    """
    A dlt resource to extract data from the Pokemon REST API.
    This function fetches data from the Location endpoint and yields the response.
    Args:
        None
    Yields:
        Generator: Yields the response object from the Pokemon REST API.
    """
    url = "https://pokeapi.co/api/v2/location"
    response = requests.get(url)
    response.raise_for_status()
    yield response.json()
@dlt.source
def pokeapi_source():
    """
    A dlt source to combine multiple resources from the Pokemon REST API.
    """
    return [
        pokemon_resource(),
        berry_resource(),
        location_resource()
    ]
@dg.multi_asset(
    outs={
        "pokemon": dg.AssetOut(
            key=[ # asset key becomes the table name in target DB
                "poke_api_3",
                "pokemon_3",
            ],
            description="General Pokemon data", # description associated with asset, viewable in Dagster UI
        ),
        "berry": dg.AssetOut(
            key=[
                "poke_api_3",
                "berry_3",
            ],
            description="Berry data which provide HP and status condition restoration, stat enhancement, and even damage negation when eaten by Pokémon",
        ),
        "location": dg.AssetOut(
            key=[
                "poke_api_3",
                "location_3",
            ],
            description="Locations that exist within Pokemon games",
        ),
    },
    group_name="dltHub__poke_3",
    compute_kind="dlt",
)
def load_pokemon_data_3():
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_pokemon_3",
        destination="duckdb",
    )
    load_info = pipeline.run(pokeapi_source(), dataset_name="poke_rest_api_3", write_disposition='replace',)
    print(load_info)
    # when an op is defined to have multiple outputs, Dagster expects the function
    # to either yield each output individually or return a tuple containing a value for each output
    return (
        dg.Output(value=load_info[0]), # returning dlt load_info object corresponding to each resource (pokemon)
        dg.Output(value=load_info[1]), # berry
        dg.Output(value=load_info[2]), # location
    )