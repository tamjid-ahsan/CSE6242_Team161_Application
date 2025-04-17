# README

## Pre-requisite

- [`poetry`](https://python-poetry.org/) for env management
  - Setup for your OS. <i>[Official Instructions](https://python-poetry.org/docs/#installing-with-the-official-installer)</i>.

## Install required packages

```bash
cat requirements.txt | xargs -n 1 poetry add
```

## Run application

navigate to app dir. `cd app`

```
# folder structure
.
├── app
│   ├── app.py
│   ├── data
│   │   ├── cleaned_2016_election_results.csv
│   │   ├── cleaned_merged_data.csv
│   │   ├── rentals_homeValue_homeValueForecast.csv
│   │   ├── us-counties-fips.json
│   │   ├── us-states.json
│   │   ├── zip_codes.geojson
│   │   └── zipcodes_clean.csv
│   ├── ml
│   │   ├── ml_pred_sample.csv
│   │   ├── ml_pred_sample.json
│   │   └── put_ml_model_here.txt
│   ├── utils.py
│   └── www
│       └── assets
│           ├── georgia-tech-yellow-jackets-logo-black-and-white.png
│           ├── georgia-tech-yellow-jackets-logo-png-transparent.png
│           ├── gps.png
│           ├── usa-map.png
│           └── volatility.png
├── LICENSE
├── poetry.lock
├── pyproject.toml
├── README.md
└── requirements.txt

```

use `pwd` to confirm that you are at the right path.

```bash
# will look something like this
/Users/<your/file/path>/app
```

run this to start app. This will run a development server with auto-reload.
```bash
poetry run python -m shiny run --port 63253 --reload --autoreload-port 63254 ./app.py
```

run without auto-reload flag (`--autoreload-port 63254`) for demo.