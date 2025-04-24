# Previewing Dagster's new dg CLI + dltHub + DuckDB local UI

### This project's main utilities:
- Showing the different ways of reading from a single REST API with multiple endpoints using dltHub
- Materialize the extraction of these endpoints as [Dagster multi-assets](https://docs.dagster.io/guides/build/assets/defining-assets#multi-asset)
- Utilize the [new dg CLI interface](https://github.com/dagster-io/dagster/discussions/28472) to scaffold a project
- Utilize the[ new duckdb CLI to interact with data locally](https://duckdb.org/2025/03/12/duckdb-ui.html)

### Prerequisites 
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (`>=0.6.7`)
2. Install the experimental preview of [dg](https://docs.dagster.io/guides/labs/dg/) (`>=0.26.6`)
3. Install [DuckDB](https://duckdb.org/docs/installation/?version=stable&environment=cli&platform=macos&download_method=package_manager) `(>= 1.2.1)`
4. Install [yarn](https://classic.yarnpkg.com/lang/en/docs/install/#mac-stable) for running Dagster's local documentation site `(>=1.22.22)`

**Note:** To launch the DuckDB Local UI: Run `duckdb -ui` in your terminal

# Getting started  
1. Clone the repo locally
2. Run `uv sync`
3. Run `source .venv/bin/activate`

# Basic dg commands

`dg docs serve`
- Serve a local Dagster dg documentation site

`dg list defs`
- List asset definitions

`dg check defs`
- Check for validity of definitions

`dg launch --assets <asset_key>`
- Materialize an asset from the CLI

`dg scaffold asset assets/dbt/dbt_assets.py`
- Scaffold an example dbt asset definition within `defs/assets/dbt`

`dg dev`
- Run the Dagster webserver/daemon to interact with, view, and launch your Assets in the UI
- Drop in replacement for `dagster dev`

# Advantages of the dg CLI
1. Easy to scafold and organize your Dagster project
2. Python venv management with `dg` is integrated with `uv` out of the box
3. Automatic definitions discovery
  - As soon as you create an asset definition, it will be recognized without manual import into a top-level `dg.Definitions` object
4. CLI-first development that makes developing more streamlined and fun!
  - `list`, `check`, `launch`, etc
5. Component framework and YML integration for building low/medium code, declarative pipelines 
  - Lowers the technical bar for contributors to a Dagster project