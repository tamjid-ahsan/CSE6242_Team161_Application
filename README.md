# US Relocation Recommendation Tool - A Shiny App

## CSE6242-Team161-Spring 2025

Find your ideal location based on personalized preferences. An interactive Python Shiny application for dashboarding U.S. State-county-zip code‑level information, e.g., home‑value forecasts, and rental trends, and recommendation for relocation using machine learning predictions.

> Application available at: [https://tamjid-ahsan-cse6242-team161-application.share.connect.posit.cloud](https://tamjid-ahsan-cse6242-team161-application.share.connect.posit.cloud/). 

This is the repo used as source code for the application hosted on [posit cloud](https://connect.posit.cloud/). This project is part of the deliverable of [OMS Analytics program of Georgia Institute of Technology](https://pe.gatech.edu/degrees/analytics).

<b>Team</b>: Hannah Johnston, Hannah Johnson, Avery Wall, Tamjid Ahsan, George Dilip, Cheston Husein.

## Tech Stack

- **Language**: `Python`, `HTML`, `JavaScript`
- **Framework**: [`Shiny`](https://shiny.posit.co/py/#install) for Python
- **Environment**: `Poetry` for dependency management  
- **Libraries**: `pandas`, `geopandas`, `plotly`, `scikit-learn`, etc.


## Pre-requisite

- [`poetry`](https://python-poetry.org/) for env management
  - Setup for your OS. <i>[Official Instructions](https://python-poetry.org/docs/#installing-with-the-official-installer)</i>.

## Local Installation

Clone the repo, install packages required for the application using poetry.

```bash
git clone https://github.com/tamjid-ahsan/CSE6242_Team161_Application.git
cd CSE6242_Team161_Application
poetry install
```

  > ### Install from `requirements.txt`

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
```
# repo folder structure


```

## Data source

```

```