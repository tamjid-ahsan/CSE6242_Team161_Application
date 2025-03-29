# app.py
from shiny import App, render, ui, reactive
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import math
import requests

# ----------------------------
# Helper Function: Haversine
# ----------------------------
def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    km = 6371 * c
    return km

# ----------------------------
# Sample Data for 10 States
# ----------------------------
data = [
    {"state": "California", "state_code": "CA", "income": 8, "cost_of_living": 7, "crime_rate": 4, "job_opportunities": 9, "climate": 8, "lat": 36.7783, "lon": -119.4179},
    {"state": "Texas",      "state_code": "TX", "income": 7, "cost_of_living": 5, "crime_rate": 6, "job_opportunities": 8, "climate": 7, "lat": 31.9686, "lon": -99.9018},
    {"state": "New York",   "state_code": "NY", "income": 9, "cost_of_living": 6, "crime_rate": 5, "job_opportunities": 9, "climate": 6, "lat": 42.1657, "lon": -74.9481},
    {"state": "Florida",    "state_code": "FL", "income": 6, "cost_of_living": 6, "crime_rate": 7, "job_opportunities": 7, "climate": 9, "lat": 27.9944, "lon": -81.7603},
    {"state": "Illinois",   "state_code": "IL", "income": 7, "cost_of_living": 5, "crime_rate": 6, "job_opportunities": 7, "climate": 6, "lat": 40.0,    "lon": -89.0},
    {"state": "Pennsylvania","state_code": "PA", "income": 7, "cost_of_living": 6, "crime_rate": 5, "job_opportunities": 7, "climate": 5, "lat": 41.2033, "lon": -77.1945},
    {"state": "Ohio",       "state_code": "OH", "income": 6, "cost_of_living": 5, "crime_rate": 6, "job_opportunities": 7, "climate": 5, "lat": 40.3675, "lon": -82.9962},
    {"state": "Georgia",    "state_code": "GA", "income": 7, "cost_of_living": 6, "crime_rate": 5, "job_opportunities": 7, "climate": 8, "lat": 32.1656, "lon": -82.9001},
    {"state": "North Carolina", "state_code": "NC", "income": 7, "cost_of_living": 6, "crime_rate": 5, "job_opportunities": 7, "climate": 7, "lat": 35.7596, "lon": -79.0193},
    {"state": "Michigan",   "state_code": "MI", "income": 6, "cost_of_living": 5, "crime_rate": 7, "job_opportunities": 6, "climate": 4, "lat": 44.3148, "lon": -85.6024},
]
df = pd.DataFrame(data)

# ----------------------------
# Dummy Zip Code Lookup
# ----------------------------
zip_lookup = {
    "10001": {"lat": 40.750742, "lon": -73.99653},   # New York, NY
    "90001": {"lat": 33.973951, "lon": -118.248405},  # Los Angeles, CA
    "60601": {"lat": 41.88531,  "lon": -87.62166},    # Chicago, IL
}

# ----------------------------
# Load GeoJSON for US States
# ----------------------------
geojson_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
geojson_data = requests.get(geojson_url).json()

# ----------------------------
# Define the UI with a fluid layout (three rows)
# ----------------------------
app_ui = ui.page_fluid(
    # First row: Inputs and Map
    ui.row(
        ui.column(3,
            ui.input_text("zip_code", "Enter Zip Code:", placeholder="e.g., 10001"),
            ui.input_slider("weight_income", "Weight for Income:", 0, 1, 0.2, step=0.1),
            ui.input_slider("weight_cost", "Weight for Cost of Living:", 0, 1, 0.2, step=0.1),
            ui.input_slider("weight_crime", "Weight for Crime Rate:", 0, 1, 0.2, step=0.1),
            ui.input_slider("weight_job", "Weight for Job Opportunities:", 0, 1, 0.2, step=0.1),
            ui.input_slider("weight_climate", "Weight for Climate:", 0, 1, 0.2, step=0.1)
        ),
        ui.column(9,
            ui.output_ui("us_map")
        )
    ),
    # Second row: Dual-Axis Line Chart
    ui.row(
        ui.column(8,
            ui.output_ui("line_chart")
        ),
        ui.column(4,
            ui.output_ui("info_box")
        )
    ),
    # # Third row: Information Box
    # ui.row(
    #     ui.column(12,
    #         ui.output_ui("info_box")
    #     )
    # ),
    title="US Relocation Recommendation Tool"
)

# ----------------------------
# Define the Server Logic
# ----------------------------
def server(input, output, session):
    @reactive.Calc
    def compute_scores():
        # Retrieve current weight values from the inputs
        w_income  = input.weight_income()
        w_cost    = input.weight_cost()
        w_crime   = input.weight_crime()
        w_job     = input.weight_job()
        w_climate = input.weight_climate()
        
        # Compute a base score as a weighted sum of the factors.
        df["base_score"] = (w_income * df["income"] +
                            w_cost * df["cost_of_living"] +
                            w_crime * df["crime_rate"] +
                            w_job * df["job_opportunities"] +
                            w_climate * df["climate"])
        
        # Adjust scores based on proximity if a valid zip code is entered.
        zip_code = input.zip_code().strip()
        if zip_code in zip_lookup:
            zip_lat = zip_lookup[zip_code]["lat"]
            zip_lon = zip_lookup[zip_code]["lon"]
            multipliers = []
            for idx, row in df.iterrows():
                distance = haversine(zip_lat, zip_lon, row["lat"], row["lon"])
                multiplier = math.exp(-distance / 500)  # exponential decay
                multipliers.append(multiplier)
            df["proximity_multiplier"] = multipliers
            df["final_score"] = df["base_score"] * (1 + df["proximity_multiplier"])
        else:
            df["final_score"] = df["base_score"]
        
        return df

    @output
    @render.ui
    def us_map():
        scored_df = compute_scores()
        # Build the choropleth map using Plotly.
        fig = px.choropleth(
            scored_df,
            locations="state_code",
            locationmode="USA-states",
            color="final_score",
            scope="usa",
            color_continuous_scale="Blues",
            labels={"final_score": "Score"},
            hover_name="state",
            hover_data={"state_code": False, "final_score": True}
        )
        fig.update_layout(title_text="US Regions Recommendation",
                          geo=dict(lakecolor='rgb(255, 255, 255)'))
        # Wrap the Plotly figure HTML in a Shiny UI element.
        return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False))
    
    @output
    @render.ui
    def line_chart():
        # Generate dummy time series data (2010-2020)
        years = list(range(2010, 2021))
        # Dummy house prices and rental prices (with simple linear trends)
        house_prices = [200 for year in years]
        rental_prices = [100 + (year - 2010) * 2 for year in years]
        df_trends = pd.DataFrame({
            "Year": years,
            "House Price": house_prices,
            "Rental Price": rental_prices,
        })
        
        # Create a dual-axis plot using Plotly's subplots.
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add house price trace on primary y-axis.
        fig.add_trace(
            go.Scatter(x=df_trends["Year"], y=df_trends["House Price"], mode="lines+markers", name="House Price"),
            secondary_y=False
        )
        # Add rental price trace on secondary y-axis.
        fig.add_trace(
            go.Scatter(x=df_trends["Year"], y=df_trends["Rental Price"], mode="lines+markers", name="Rental Price"),
            secondary_y=True
        )
        # Set titles and axis labels.
        selected_zip = input.zip_code().strip() if input.zip_code().strip() in zip_lookup else "N/A"
        fig.update_layout(
            title=f"House Price and Rental Trends for Zip Code: {selected_zip}",
            xaxis_title="Year"
        )
        fig.update_yaxes(title_text="House Price (USD)", secondary_y=False)
        fig.update_yaxes(title_text="Rental Price (USD)", secondary_y=True)
        
        return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False))
    
    @output
    @render.ui
    def info_box():
        # Use the selected zip code if valid; otherwise, default to "N/A"
        selected_zip = input.zip_code().strip() if input.zip_code().strip() in zip_lookup else "N/A"
        # Dummy additional information
        info = {
            "Population": "500,000",
            "Climate": "Temperate",
            "Median Income": "$55,000",
            "Cost of Living": "Moderate",
            "Job Opportunities": "Abundant"
        }
        info_html = f"<h3>Additional Information for Zip Code: {selected_zip}</h3><ul>"
        for key, value in info.items():
            info_html += f"<li><b>{key}:</b> {value}</li>"
        info_html += "</ul>"
        return ui.HTML(info_html)

# ----------------------------
# Create the Shiny App
# ----------------------------
app = App(app_ui, server)
