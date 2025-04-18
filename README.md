# US Relocation Recommendation Tool - A Shiny App

## CSE6242-Team161-Spring 2025

Find your ideal location based on personalized preferences. An interactive Python Shiny application for dashboarding U.S. State-county-zip code‑level information, e.g., home‑value forecasts, and rental trends, and recommendation for relocation using machine learning predictions.

> Application available at: [https://tamjid-ahsan-cse6242-team161-application.share.connect.posit.cloud](https://tamjid-ahsan-cse6242-team161-application.share.connect.posit.cloud/). 

This repo used as source code for the application hosted on [posit cloud](https://connect.posit.cloud/).
This project is part of the deliverables for CSE6242 of [OMS Analytics program of Georgia Institute of Technology](https://pe.gatech.edu/degrees/analytics).

<b>Team</b>: Hannah Johnston, Hannah Johnson, Avery Wall, Tamjid Ahsan, George Dilip, Cheston Husein.

## Tech Stack

- **Language**: `Python` >=3.12,<3.13.0, `HTML`, `JavaScript`
- **Framework**: [`Shiny`](https://shiny.posit.co/py/#install) for Python
- **Environment**: `Poetry` for dependency management  
- **Libraries**: `pandas`, `geopandas`, `plotly`, `scikit-learn`, etc.

## Pre-requisite

> Note: Below commands are for [PoP!_OS](https://system76.com/pop/). A free and open-source Linux distribution, based on Ubuntu (A Debian based OS).
- `Python` >=3.12,<3.13.0
  - Check python version `python --version`
  - install proper python version if required python is not available

    ```bash
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.12
    ```

  -  
- [`poetry`](https://python-poetry.org/) =2.0.0,<3.0.0, for env management
  - Setup for your OS following the official instructions. <i>[Official Instructions](https://python-poetry.org/docs/#installing-with-the-official-installer)</i>.

    - install [pipx](https://pipx.pypa.io/stable/installation/)
  
      ```
      sudo apt update
      sudo apt install pipx
      pipx ensurepath
      ```

    - install poetry, and ensure it is in global path

      ```bash
      pipx install poetry
      ```

    - go to a new terminal shell and type, this will show poetry version (e.g., `Poetry (version 2.1.2)`)

      ```bash
      poetry --version
      ```

## Local Installation

Clone the repo, install packages required for the application using poetry.

```bash
git clone https://github.com/tamjid-ahsan/CSE6242_Team161_Application.git
cd CSE6242_Team161_Application
```

install packages required for the application

```bash
poetry install --no-root  
```

>> if errored because of python compatibility, use this to us proper python version `poetry env use 3.12`

activate env

```bash
poetry env activate
```

  > ### [Alternative] Install from `requirements.txt`, if using `poetry init` to setup poetry fresh, go through `poetry init` routine. Don't add packages. After init, run this.

  ```bash
  cat requirements.txt | xargs -n 1 poetry add
  ```

## Usage - Run application

Navigate to app dir.

```bash
cd app
```

use `pwd` to confirm that you are at the right path.

```bash
# will look something like this on a Unix system
/Users/<your/file/path>/app
```

run this to start app in <i>development</i> mode. This will run a development server with auto-reload.

```bash
poetry run python -m shiny run --port 63253 --reload --autoreload-port 63254 ./app.py
```
Then open `http://localhost:63253` in your browser.

> run without `auto-reload` flag (`--autoreload-port 63254`) for demo.

## Project Structure

```bash
# repo folder structure
.
├── app
│   ├── __init__.py
│   ├── app.py                                    # application entry point
│   ├── data
│   │   ├── cleaned_2016_election_results.csv     # political data acquired from NYT
│   │   ├── cleaned_merged_data.csv               # ml clustering output
│   │   ├── rentals_homeValue_homeValueForecast.csv # rental data acquired from Zillow
│   │   ├── us-counties-fips.json                 # used for map
│   │   ├── us-states.json                        # used for map
│   │   ├── zip_codes.geojson                     # used for map
│   │   └── zipcodes_clean.csv                    # used to match zipcode data
│   ├── index.html                                # boilerplate 
│   ├── ml.py                                     # user preference prediction algorithm
│   ├── utils.py                                  # helper functions
│   └── www                                       # web assets
│       ├── assets
│       │   ├── georgia-tech-yellow-jackets-logo-black-and-white.png
│       │   ├── georgia-tech-yellow-jackets-logo-png-transparent.png
│       │   ├── gps.png
│       │   ├── usa-map.png
│       │   └── volatility.png
│       └── favicon.ico
├── LICENSE
├── poetry.lock
├── pyproject.toml                              # poetry file
├── README.md
└── requirements.txt                            # application dependency

```

## Data source

1. Zillow: [Housing Data](https://www.zillow.com/research/data/)
2. NYT: Political demography data
3. US Census: Population/demographic Data
4. Climate
5. Education
6. Health
7. Income & Tax
8. GeoData: [Plotly FIPS data](https://github.com/plotly/datasets/blob/master/geojson-counties-fips.json), github

## Known Issue

- map container sometimes resets to wrong aspect ratio.
