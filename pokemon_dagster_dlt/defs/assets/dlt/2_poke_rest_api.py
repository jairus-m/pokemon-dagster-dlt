"""
This example uses the dagster-dlt library within the Dagster framework (official integration) to materialize
multi-assets from 3 endpoints of a single REST API source.

This example may have a bug. The "dlt" resource specified in pokemon_dagster_dlt/definitions.py is not being 
recognized. View comments at the bottom for more detail.
"""

# import dagster as dg
# import dlt
# from dlt.extract.resource import DltResource
# from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
# from dlt.sources.rest_api import rest_api_source
# from collections.abc import Iterable

# pokemon_source = rest_api_source(
#     {
#         "client": {"base_url": "https://pokeapi.co/api/v2/"},
#         "resource_defaults": {
#             "endpoint": {
#                 "params": {
#                     "limit": 1000,
#                 },
#             },
#         },
#         "resources": [
#             "pokemon",
#             "berry",
#             "location",
#         ],
#     }
# )

# class CustomDagsterDltTranslator(DagsterDltTranslator):
#      def get_asset_key(self, resource: DltResource) -> dg.AssetKey:
#          """Overrides asset key to be the dlt resource name with a 'pokemon' prefix."""
#          return dg.AssetKey(f"{resource.name}").with_prefix("poke_api_2")

#      def get_deps_asset_keys(self, resource: DltResource) -> Iterable[dg.AssetKey]:
#          """Overrides upstream asset key to be a single source asset."""
#          return []

# @dlt_assets(
#     dlt_source=pokemon_source,
#     dlt_pipeline=dlt.pipeline(
#         pipeline_name="example_2",
#         dataset_name="poke_rest_api_2",
#         destination="duckdb",
#     ),
#     group_name="dltHub__github_2",
#     dagster_dlt_translator=CustomDagsterDltTranslator(),
# )

# def load_pokemon_2(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
#     yield from dlt.run(context=context)

"""
Running `dg check defs`:

------------------------

2025-03-29 14:55:29 -0700 - dagster - ERROR - Validation failed for code location pokemon-dagster-dlt:

dagster._core.errors.DagsterInvalidDefinitionError: resource with key 'dlt' required by op 'load_pokemon_2' was not provided. Please provide a ResourceDefinition to key 'dlt', or change the required key to one of the following keys which points to an ResourceDefinition: ['io_manager']

Stack Trace:
  [15 dagster system frames hidden, run with --verbose to see the full stack trace]

2025-03-29 14:55:29 -0700 - dagster - ERROR - Validation for 1 code locations failed.

------------------------

This error comes up even though "dlt" is defined in defs/resources/__init__.py and imported into the defs object.

in defs/definitions.py:

defs = load_defs(
    defs_root=pokemon_dagster_dlt.defs,
    resources={
        "dlt": resources.dlt_resource
    },    
)

This follows the docs and works fine using the latest dagster library (not dg CLI).
"""