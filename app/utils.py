from math import radians, sin, cos, sqrt, atan2
import re
import pandas as pd
from datetime import datetime
import geopandas as gpd
import json
import plotly.express as px


def usMapRender(df):
    with open("./data/us-states.json", "r") as f:
        us_state = json.load(f)

    with open("./data/us-counties-fips.json", "r") as f:
        us_counties = json.load(f)

    with open("./data/zip_codes.geojson", "r") as f:
        us_zip = json.load(f)

    gdf_state = gpd.GeoDataFrame.from_features(us_state["features"])
    gdf_counties = gpd.GeoDataFrame.from_features(us_counties["features"])
    gdf_zip = gpd.GeoDataFrame.from_features(us_zip["features"])

    df["cluster"] = df["cluster"].astype("string")

    fig = (
        px.scatter_map(
            df,
            lat="lat",
            lon="lon",
            color="cluster",
            hover_name='zip',
            custom_data=['zip'],
            # hover_data=["cluster"],
            category_orders={
                "cluster": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17",
                            "18", "19", "20"]
            },
            labels={"zip": "Zip Code", "cluster": "Cluster"},
            # hover_data={"state_code": False, "final_score": True},
            color_discrete_sequence=px.colors.qualitative.Plotly,
            template="plotly",
            height=700
        )
            .update_traces(marker={"size": 3},
                           hovertemplate="<b>Zip Code:</b> %{hovertext}<extra></extra>"
                           )
            .update_layout(
            # geo = dict(
            #     scope='usa',
            #     projection_type='albers usa',
            #     showland = True
            # ),
            map={
                "style": "open-street-map",
                "zoom": 3,
                # "maxzoom": 5,
                "layers": [
                    {
                        "source": json.loads(gdf_state.geometry.to_json()),
                        "below": "traces",
                        "type": "line",
                        "color": "red",
                        "line": {"width": 2},
                    },
                    {
                        "source": json.loads(gdf_counties.geometry.to_json()),
                        "below": "traces",
                        "type": "line",
                        "color": "grey",
                        "line": {"width": 1.5},
                        "opacity": .5,
                    },
                    {
                        "source": json.loads(gdf_zip.geometry.to_json()),
                        "below": "traces",
                        "type": "line",
                        "color": "blue",
                        "line": {"width": .3},
                        "opacity": .5,
                    }
                ],
            },
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            annotations=[
                dict(
                    text="<b>Click on Zip Codes for details.</b>",
                    align='right',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=0.05,
                    xanchor='left',
                    yanchor='top',
                    font=dict(
                        size=12
                    )
                )
            ],
            legend=dict(
                # title=dict(
                #     font=dict(
                #         size=8
                #     )
                # ),
                orientation="v",
                x=0.01,  # Slightly inset from the absolute left edge (0)
                y=0.99,  # Slightly down from the absolute top edge (1)
                xanchor='left',  # Anchor the legend's left edge to the x coordinate
                yanchor='top',  # Anchor the legend's top edge to the y coordinate
                bgcolor='rgba(255,255,255,0.85)',  # Add semi-transparent background
                bordercolor='Grey',  # Add border
                borderwidth=1  # Border width
            )
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
    pattern = r'^\d{5}(-\d{4})?$'
    return bool(re.match(pattern, zip))


def collectingLineGraphData(zip):
    zips = int(zip)
    df = pd.read_csv('./data/rentals_homeValue_homeValueForecast.csv')
    # df = pd.read_csv('./data/rentals_homeValue_homeValueForecast.csv')
    df.rename(columns={"RegionName": "zipcode"}, inplace=True)
    m_df = df.query("zipcode == @zips")[["date", "Rentals", "HomeValue"]].dropna()
    return m_df


def collectingLineGraphData_HomeValueForecast(zip):
    zips = int(zip)
    df = pd.read_csv('./data/rentals_homeValue_homeValueForecast.csv')
    # df = pd.read_csv('./data/rentals_homeValue_homeValueForecast.csv')

    df.rename(columns={"RegionName": "zipcode"}, inplace=True)
    # m_df = df.query("zipcode == @zips")[["date", "Rentals", "HomeValueForecast"]].dropna()
    forecast_info = df.query("zipcode == @zips")[["date", 'HomeValueForecast']].dropna()
    if forecast_info.empty:
        return [[], '']
    else:
        first_date_str = forecast_info.iloc[0]["date"]
        time_stamp = datetime.strptime(first_date_str, '%Y-%m-%d')
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


def calculate_top_suggestion(zipcode, radius):
    suggested_zip = []
    counter = 0
    df = pd.read_csv("./ml/ml_pred_sample.csv",
                     dtype={"zip": "str"})
    df_sorted = df.sort_values(by="prob", ascending=False)
    # Filter by ZIP code
    selected_row = df_sorted[df_sorted["zip"] == str(zipcode)]
    zip_lat = selected_row["lat"]
    zip_lon = selected_row["lon"]
    for index, row in df_sorted.iterrows():
        lat = row["lat"]
        lon = row["lon"]
        distance = haversine(zip_lat, zip_lon, lat, lon)

        if distance <= radius:
            suggested_zip.append(row['zip'])
            counter = counter + 1
            if counter == 10:
                break
    print(suggested_zip)


# 58856
def collectingZipInformation(zip):
    zipcode = int(zip)
    df = pd.read_csv('./data/cleaned_merged_data.csv')
    pol_df = pd.read_csv("./data/cleaned_2016_election_results.csv", dtype={"ZIP": "str"})
    # df = pd.read_csv('data/cleaned_merged_data.csv')
    # m_df = df.query("zip == @zipcode").T
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
            '🏙️ City': info_dict["city"],
            '📍 State': info_dict["state_name"],
            '🏷️ State ID': info_dict["state_id"],
            '👥 Population': f"{info_dict['population']:.0f}",
            '🏘️ Population density': f"{info_dict['density']:.0f}",
            '<img src="assets/gps.png" alt="County Icon" width="14" height="14" '
            'style="vertical-align:left; margin-left:0px;"> County':
                info_dict["county_name"],
            """🌦️ <abbr title="Dry Conditions:
        - Very low rainfall indicates either Arid (if warm) or Dry climates (if cooler).
        - Moderate low rainfall is classified as Semi-arid climate.

        Cold Climates:
        - Extremely low temperatures (below 32°F) with high snowfall yield a Polar climate, otherwise Subarctic climate.
        - For temperatures between 32°F and 45°F, high snowfall leads to a Tundra classification, otherwise Continental climates.

        Moderate Climates:
        - Average temperatures between 45°F and 60°F are differentiated by rainfall amounts into Humid continental, Temperate marine, or Temperate climates.

        Warm Climates: - Temperatures above 60°F are further classified by rainfall into Mediterranean, 
        Tropical monsoon, Humid subtropical, or Tropical rainforest climate."> Climate</abbr>""":
                f"{classify_climate(info_dict['avg_temp'], info_dict['avg_snow'], info_dict['avg_rain'])}",
            '🌡️ Average temperature': f"{info_dict['avg_temp']:.2f}° F",
            '❄️ Average snowfall': f"{info_dict['avg_snow']:.2f} inch << THIS NEEDS CONFIRMATION",
            '🌧️ Average precipitation': f"{info_dict['avg_rain']:.2f} mm << THIS NEEDS CONFIRMATION",
            '<abbr title="Assuming 2 party only"><img src="assets/usa-map.png" alt="Map Icon" width="14" height="14" '
            'style="vertical-align:left; margin-left:0px;"> Political Affiliation</abbr>':
                (
                    f"Democrat: <span style='color:blue'> ~{pol_df[pol_df['ZIP'] == str(zipcode)]['dem_pct'].values[0]:.2%}</span>; "
                    f"Republican: <span style='color:red'> ~{pol_df[pol_df['ZIP'] == str(zipcode)]['rep_pct'].values[0]:.2%}</span>"
                    if not pol_df[pol_df['ZIP'] == str(zipcode)].empty
                    else "Political affiliation data not available."
                ),
            '<img src="assets/volatility.png" alt="Map Icon" width="14" height="14" '
            'style="vertical-align:left; margin-left:0px;"> Political Affiliation Volatility':
                f"{info_dict['dem_lead_std']:.2f} << THIS NEEDS EXPLANATION",
            '🎓 Post-secondary institutions': info_dict['num_postsecondary_institutions'],
            '🩺 Health rating': f"{info_dict['health_rating']} << THIS NEEDS EXPLANATION",
            '💰 Average salary/earner': f"{info_dict['avg_salary_per_earner']:,.0f}K",
            f'🧭 Zip codes in the county ({len(df.query("""county_name == @info_dict["county_name"]""")["zip"].unique())})':
                ", ".join([str(x) for x in df.query("""county_name == @info_dict["county_name"]""")["zip"].unique()])
        }
        return information_dict
