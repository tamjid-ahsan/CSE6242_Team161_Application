from math import radians, sin, cos, sqrt, atan2
import re
import pandas as pd
from datetime import datetime
import geopandas as gpd
import json
import numpy as np
import plotly.express as px
import os

BASE_DIR = os.path.dirname(__file__)        # /cloud/project/app
DATA_DIR = os.path.join(BASE_DIR, "data")   # /cloud/project/app/data


def usMapRender(df):
    with open(
        os.path.join(DATA_DIR, "us-states.json"), "r"
    ) as f:  # "./data/us-states.json"
        us_state = json.load(f)

    with open(
        os.path.join(DATA_DIR, "us-counties-fips.json"), "r"
    ) as f:  # "./data/us-counties-fips.json"
        us_counties = json.load(f)

    with open(
        os.path.join(DATA_DIR, "zip_codes.geojson"), "r"
    ) as f:  # "./data/zip_codes.geojson"
        us_zip_full = json.load(f)

    # Filter zip codes to only those in the dataframe
    # Convert df zip codes to a set for faster lookup
    df_zip_codes = set(df["zip"].astype(str))

    # Filter the features list to only include zip codes in df
    filtered_features = [
        feature
        for feature in us_zip_full["features"]
        if feature["properties"]["ZCTA5CE10"] in df_zip_codes
    ]

    # Create a new geojson object with only the filtered features
    us_zip = {"type": us_zip_full["type"], "features": filtered_features}

    gdf_state = gpd.GeoDataFrame.from_features(us_state["features"])
    gdf_counties = gpd.GeoDataFrame.from_features(us_counties["features"])
    gdf_zip = gpd.GeoDataFrame.from_features(us_zip["features"])

    # Merge rank data from df into gdf_zip
    gdf_zip["ZCTA5CE10"] = gdf_zip["ZCTA5CE10"].astype(str)
    df_for_join = df.copy()
    df_for_join["zip"] = df_for_join["zip"].astype(str)

    # Join the dataframes
    gdf_zip = gdf_zip.merge(
        df_for_join[["zip", "rank"]], left_on="ZCTA5CE10", right_on="zip", how="left"
    )

    # Create color scale based on rank
    min_rank = df["rank"].min()
    max_rank = df["rank"].max()
    colorscale = px.colors.sequential.Viridis

    # Create bins for ranks to apply different colors
    n_bins = 10  # Number of color bins
    bins = np.linspace(min_rank, max_rank, n_bins + 1)

    # Create layers for each bin
    fill_layers = []

    for i in range(n_bins):
        # Filter data for this bin
        lower = bins[i]
        upper = bins[i + 1]

        # For the last bin, include the upper bound
        if i == n_bins - 1:
            bin_gdf = gdf_zip[(gdf_zip["rank"] >= lower) & (gdf_zip["rank"] <= upper)]
        else:
            bin_gdf = gdf_zip[(gdf_zip["rank"] >= lower) & (gdf_zip["rank"] < upper)]

        # Skip if empty
        if bin_gdf.empty:
            continue

        # Get color for this bin (normalize between 0 and 1)
        bin_pos = (i + 0.5) / n_bins  # Center position in the bin

        # Get color from viridis colorscale
        color_idx = int(bin_pos * (len(colorscale) - 1))
        color = (
            colorscale[color_idx][1]
            if isinstance(colorscale[0], (list, tuple))
            else colorscale[color_idx]
        )

        # Create layer for this bin
        if not bin_gdf.empty:
            layer = {
                "source": json.loads(bin_gdf.geometry.to_json()),
                "below": "traces",
                "type": "fill",
                "color": color,
                "opacity": 0.5,
            }
            fill_layers.append(layer)

    # Add state boundaries layer
    state_layer = {
        "source": json.loads(gdf_state.geometry.to_json()),
        "below": "traces",
        "type": "line",
        "color": "red",
        "line": {"width": 2},
    }

    # Add county boundaries layer
    county_layer = {
        "source": json.loads(gdf_counties.geometry.to_json()),
        "below": "traces",
        "type": "line",
        "color": "black",
        "line": {"width": 0.2},
        "opacity": 0.3,
    }

    # # Add zip boundaries layer
    # zip_codes_layer = {
    #     "source": json.loads(gdf_zip.geometry.to_json()),
    #     "below": "traces",
    #     "type": "line",
    #     "color": "black",
    #     "line": {"width": .2},
    #     "opacity": 0.3,
    # }

    # Combine all layers
    all_layers = [state_layer, county_layer] + fill_layers

    fig = (
        px.scatter_map(
            df,
            lat="lat",
            lon="lng",
            color="rank",
            hover_name="zip",
            custom_data=[
                "zip",
                "city",
                "state_name",
                "population",
                "avg_temp",
                "health_rating",
                "avg_salary_per_earner",
                "recent_rental_price",
                "rank",
            ],
            labels={"zip": "Zip Code", "rank": "Rank"},
            color_continuous_scale=colorscale,
            template="plotly",
            height=700,
        )
        .update_traces(
            marker={
                "size": df["density"],
                "sizemode": "area",
                "sizeref": 2.0 * max(df["density"]) / (15.0**2),
                "sizemin": 2,
            },
            hovertemplate=(
                "<b>%{customdata[1]}</b>, %{customdata[2]}<br><br>"
                "Population: %{customdata[3]}<br>"
                "Avg Temp: %{customdata[4]}°F<br>"
                "Health Rating: %{customdata[5]}<br>"
                "Avg Salary: $%{customdata[6]:,.0f}K<br>"
                "Rental Price: $%{customdata[7]:,.0f}<br>"
                "Rank: %{customdata[8]}"
                "<extra></extra>"
            ),
        )
        .update_layout(
            map={
                "style": "open-street-map",
                "zoom": 3,
                "layers": all_layers,
            },
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            annotations=[
                dict(
                    text="<b>Click on Zip Codes for details.</b>",
                    align="right",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=0.05,
                    xanchor="left",
                    yanchor="top",
                    font=dict(size=12),
                )
            ],
            coloraxis_colorbar=dict(
                title="Rank",
                thicknessmode="pixels",
                thickness=20,
                lenmode="pixels",
                len=300,
                yanchor="top",
                y=1,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="Grey",
                borderwidth=1,
            ),
        )
    )

    fig.update_layout(map_bounds={"west": -180, "east": -50, "south": 10, "north": 72})
    return fig


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.

    Parameters:
    - lat1, lon1: Latitude and longitude of the first point (in degrees)
    - lat2, lon2: Latitude and longitude of the second point (in degrees)

    Returns:
    - Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def checkZip(zip):
    pattern = r"^\d{5}(-\d{4})?$"
    return bool(re.match(pattern, zip))


def collectingLineGraphData(zip):
    zips = int(zip)
    df = pd.read_csv(
        os.path.join(DATA_DIR, "rentals_homeValue_homeValueForecast.csv")
    )  # './data/rentals_homeValue_homeValueForecast.csv'
    df.rename(columns={"RegionName": "zipcode"}, inplace=True)
    m_df = df.query("zipcode == @zips")[["date", "Rentals", "HomeValue"]].dropna()
    return m_df


def collectingLineGraphData_HomeValueForecast(zip):
    zips = int(zip)
    df = pd.read_csv(
        os.path.join(DATA_DIR, "rentals_homeValue_homeValueForecast.csv")
    )  # './data/rentals_homeValue_homeValueForecast.csv'

    df.rename(columns={"RegionName": "zipcode"}, inplace=True)
    forecast_info = df.query("zipcode == @zips")[["date", "HomeValueForecast"]].dropna()
    if forecast_info.empty:
        return [[], ""]
    else:
        first_date_str = forecast_info.iloc[0]["date"]
        time_stamp = datetime.strptime(first_date_str, "%Y-%m-%d")
        return [forecast_info.to_dict(orient="records")[0], time_stamp]


def classify_climate(avg_temp, avg_snow, avg_rain):
    """
    Classify the climate category based on average temperature, snowfall, and rainfall.

    Parameters:
      avg_temp: Average annual temperature (in Fahrenheit)
      avg_snow: Average annual snowfall (in inches)
      avg_rain: Average annual rainfall (in inches)

    Returns:
      A string representing one of the following climate categories:
        - Mediterranean
        - Polar climate
        - Tropical rainforest climate
        - Tundra
        - Humid continental
        - Humid subtropical
        - Arid
        - Continental climates
        - Dry climates
        - Semi-arid climate
        - Subarctic climate
        - Temperate
        - Temperate marine
        - Tropical monsoon climate
        - Climate (fallback)

    Source: https://en.wikipedia.org/wiki/Climate_of_the_United_States
    """
    # dry conditions (low precipitation)
    if avg_rain < 20:
        if avg_temp > 60:
            return "Arid"
        else:
            return "Dry climates"
    elif avg_rain < 40:
        return "Semi-arid climate"

    # classify based on temperature and snowfall
    if avg_temp < 32:
        # Extremely cold conditions
        if avg_snow >= 20:
            return "Polar climate"
        else:
            return "Subarctic climate"
    elif avg_temp < 45:
        # Cold climates
        if avg_snow >= 20:
            return "Tundra"
        else:
            return "Continental climates"
    elif avg_temp < 60:
        # Moderate climates: decide between temperate styles
        if avg_rain > 55:
            return "Humid continental"
        elif avg_rain > 45:
            return "Temperate marine"
        else:
            return "Temperate"
    else:
        # avg_temp >= 60: warmer climates
        # decide between Mediterranean and tropical variants
        if avg_temp < 70:
            # Transitional zones
            if 40 <= avg_rain <= 60:
                return "Mediterranean"
            elif avg_rain < 40:
                return "Tropical monsoon climate"
            else:
                return "Humid subtropical"
        else:  # avg_temp >= 70
            if avg_rain > 80:
                return "Tropical rainforest climate"
            elif avg_rain > 50:
                return "Humid subtropical"
            else:
                return "Tropical monsoon climate"

    # Fallback category
    return "Climate"


def calculate_top_suggestion(zipcode, radius, df_sorted):
    selected_row = df_sorted[df_sorted["zip"] == str(zipcode)]
    if selected_row.empty:
        return None
    zip_lat = selected_row["lat"]
    zip_lon = selected_row["lng"]
    df_sorted = df_sorted.copy()
    df_sorted["distance"] = df_sorted.apply(
        lambda row: haversine(zip_lat, zip_lon, row["lat"], row["lng"]), axis=1
    )
    filtered_df = df_sorted[df_sorted["distance"] <= radius]
    return filtered_df


# 58856
def collectingZipInformation(zip):
    zipcode = int(zip)
    df = pd.read_csv(
        os.path.join(DATA_DIR, "cleaned_merged_data.csv")
    )                                                                       # './data/cleaned_merged_data.csv'
    pol_df = pd.read_csv(
        os.path.join(DATA_DIR, "cleaned_2016_election_results.csv"),
        dtype={"ZIP": "str"},
    )                                                                       # "./data/cleaned_2016_election_results.csv"

    info = df.query("zip == @zipcode")[
        [
            "city",
            "state_name",
            "state_id",
            "population",
            "density",
            "county_name",
            "avg_temp",
            "avg_snow",
            "avg_rain",
            "dem_lead",
            "dem_lead_std",
            "num_postsecondary_institutions",
            "health_rating",
            "avg_salary_per_earner",
        ]
    ]
    if info.empty:
        return {}
    else:
        info_dict = info.to_dict(orient="records")[0]
        information_dict = {
            "🏙️ City": info_dict["city"],
            "📍 State": info_dict["state_name"],
            "🏷️ State ID": info_dict["state_id"],
            "👥 Population": f"{info_dict['population']:.0f}",
            "🏘️ Population density": f"{info_dict['density']:.0f}",
            '<img src="assets/gps.png" alt="County Icon" width="14" height="14" '
            'style="vertical-align:left; margin-left:0px;"> County': info_dict[
                "county_name"
            ],
            """🌦️ <abbr title="Dry Conditions:
        - Very low rainfall indicates either Arid (if warm) or Dry climates (if cooler).
        - Moderate low rainfall is classified as Semi-arid climate.

        Cold Climates:
        - Extremely low temperatures (below 32°F) with high snowfall yield a Polar climate, otherwise Subarctic climate.
        - For temperatures between 32°F and 45°F, high snowfall leads to a Tundra classification, otherwise Continental climates.

        Moderate Climates:
        - Average temperatures between 45°F and 60°F are differentiated by rainfall amounts into Humid continental, Temperate marine, or Temperate climates.

        Warm Climates: - Temperatures above 60°F are further classified by rainfall into Mediterranean, 
        Tropical monsoon, Humid subtropical, or Tropical rainforest climate."> Climate</abbr>""": f"{classify_climate(info_dict['avg_temp'], info_dict['avg_snow'], info_dict['avg_rain'])}",
            "🌡️ Average temperature": f"{info_dict['avg_temp']:.2f}° F",
            "❄️ Average snowfall": f"{info_dict['avg_snow']:.2f} inch",
            "🌧️ Average precipitation": f"{info_dict['avg_rain']:.2f} mm",
            '<abbr title="Assuming 2 party only"><img src="assets/usa-map.png" alt="Map Icon" width="14" height="14" '
            'style="vertical-align:left; margin-left:0px;"> Political Affiliation</abbr>': (
                f"Democrat: <span style='color:blue'> ~{pol_df[pol_df['ZIP'] == str(zipcode)]['dem_pct'].values[0]:.2%}</span>; "
                f"Republican: <span style='color:red'> ~{pol_df[pol_df['ZIP'] == str(zipcode)]['rep_pct'].values[0]:.2%}</span>"
                if not pol_df[pol_df["ZIP"] == str(zipcode)].empty
                else "Political affiliation data not available."
            ),
            # '<img src="assets/volatility.png" alt="Map Icon" width="14" height="14" '
            # 'style="vertical-align:left; margin-left:0px;"> Political Affiliation Volatility':
            #     f"{info_dict['dem_lead_std']:.2f} << THIS NEEDS EXPLANATION",
            "🎓 Post-secondary institutions": info_dict[
                "num_postsecondary_institutions"
            ],
            "🩺 Health rating": f"{info_dict['health_rating']} << THIS NEEDS EXPLANATION",
            "💰 Average salary/earner": f"{info_dict['avg_salary_per_earner']:,.0f}K",
            f'🧭 Zip codes in the county ({len(df.query("""county_name == @info_dict["county_name"]""")["zip"].unique())})': ", ".join(
                [
                    str(x)
                    for x in df.query("""county_name == @info_dict["county_name"]""")[
                        "zip"
                    ].unique()
                ]
            ),
        }
        return information_dict
