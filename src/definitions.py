from pathlib import Path

import src.defs
from dagster_components import load_defs

defs = load_defs(defs_root=src.defs)
