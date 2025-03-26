from pathlib import Path

import dagster_dlt.defs
from dagster_components import load_defs

defs = load_defs(defs_root=dagster_dlt.defs)
