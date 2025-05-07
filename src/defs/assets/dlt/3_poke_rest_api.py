"""
This example demonstrates a modular approach to using dlt with Dagster, explicitly defining
individual dlt resources and combining them into a source, then materializing them as Dagster assets.

Core approach:
- Uses dlt's @resource and @source decorators for explicit pipeline construction
- Implements custom API calls with requests library instead of dlt's REST API source
- Demonstrates write_disposition configuration for pipeline runs
- Shows manual resource aggregation into a dlt source

Architecture: 
- Hybrid manual implementation
Control Level: 
- High (custom code in @dlt.resource)
  - dlt: 
    - EL using @dlt.resource and @dlt.source allows for more control over EL
    - Code is less declarative and easier to customize
  - Dagster: 
    - Metadata/Dependencies are explicitly configured

Note: 
  - Adding extra comments for instruction/demo purposes.
  - The `.duckdb` file will be created in the current working directory as `rest_api_pokemon_3.duckdb`
"""

import dagster as dg
import dlt
import requests
from src.defs.utils import DUCKDB_PATH # could be an environment variable or config parameter

@dlt.resource
def pokemon_resource():
    """
    Fetches data from the PokeAPI /pokemon endpoint.
    
    Yields:
        Response JSON object
        - count: Total number of Pokemon available
        - results: List of Pokemon with name and URL
        - next: Pagination URL (not handled in this example)
    
    Raises:
        HTTPError: If the API request fails
    """
    url = "https://pokeapi.co/api/v2/pokemon"
    response = requests.get(url, params={"limit": 1000})
    response.raise_for_status()
    yield response.json()

@dlt.resource
def berry_resource():
    """
    Fetches data from the PokeAPI /berry endpoint.
    
    Returns:
        Response JSON object
        - growth_time: How long the berry takes to grow
        - max_harvest: Maximum number of berries yielded
        - size: Berry size in millimeters
        - smoothness: Smoothness characteristic
        - soil_dryness: Time it takes to dry the soil
    """
    url = "https://pokeapi.co/api/v2/berry"
    response = requests.get(url, params={"limit": 1000})
    response.raise_for_status()
    yield response.json()

@dlt.resource
def location_resource():
    """
    Fetches data from the PokeAPI /location endpoint.
    
    Returns:
        Response JSON object
        - region: Associated game region
        - names: Localized names
        - game_indices: Appearance in different game versions
    """
    url = "https://pokeapi.co/api/v2/location"
    response = requests.get(url, params={"limit": 1000})
    response.raise_for_status()
    yield response.json()

@dlt.source
def pokeapi_source():
    """
    Aggregates multiple dlt resources into a single source for pipeline processing.
    Returns:
        List[DltResource]: Contains pokemon, berry, and location resources in order
    """
    return [
        pokemon_resource(),  # First resource - will map to load_info[0]
        berry_resource(),    # Second resource - will map to load_info[1]
        location_resource()  # Third resource - will map to load_info[2]
    ]

@dg.multi_asset(
    outs={  # Define Dagster asset definitions/metadata for the 3 dlt Assets
        "pokemon": dg.AssetOut(
            key=["poke_api_3", "pokemon_3"], # Asset key prefix and name
            description="General Pokemon data retrieved from the PokeAPI /pokemon endpoint.", # Asset key description
        ),
        "berry": dg.AssetOut(
            key=["poke_api_3", "berry_3"],
            description=(
                "Berry characteristics from /berry endpoint including growth time, size, "
                "and cultivation properties. Affects Pokemon stats when consumed."
            ),
        ),
        "location": dg.AssetOut(
            key=["poke_api_3", "location_3"],
            description="In-game locations from /location endpoint with regional data and game appearances",
        ),
    },
    group_name="dltHub__poke_3", # Asset group name in Dagster UI
    compute_kind="dlt",
)
def load_pokemon_3():
    """
    Executes the dlt pipeline with custom-defined resources and materializes Dagster assets.
    
    Pipeline configuration:
    - Uses 'replace' write disposition to overwrite existing data on each run
    - Dataset name is specified at runtime rather than pipeline initialization
    - Output order matches resource order in pokeapi_source return list
    
    Returns:
        Tuple[Output, Output, Output]: Dagster Output objects for each resource's load info
    """
    # Initialize pipeline
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_pokemon_3",
        destination=dlt.destinations.duckdb(DUCKDB_PATH + "rest_api_pokemon_3.duckdb"),  
    )

    # Run pipeline with explicit dataset name and write disposition
    load_info = pipeline.run(
        pokeapi_source(),
        dataset_name="poke_rest_api_3",  # Logical dataset grouping in DuckDB
        write_disposition="replace",     # Full refresh pattern - replaces existing data
    )
    
    print(load_info)  # Contains load metrics and schema changes

    # Return outputs in same order as resources defined in pokeapi_source
    return (
        dg.Output(value=load_info[0]),  # pokemon_resource results
        dg.Output(value=load_info[1]),  # berry_resource results
        dg.Output(value=load_info[2]),  # location_resource results
    )
