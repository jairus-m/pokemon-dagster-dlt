from pathlib import Path

import pokemon_dagster_dlt.defs
from dagster_components import load_defs
from pokemon_dagster_dlt.defs import resources


defs = load_defs(
    defs_root=pokemon_dagster_dlt.defs,
    resources={
        "dlt": resources.dlt_resource
    },    
)
