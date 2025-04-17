from shiny import App, render, ui, reactive
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import math
from shinywidgets import output_widget, render_widget
from .utils import (
    checkZip, 
    collectingLineGraphData, 
    collectingZipInformation,
    collectingLineGraphData_HomeValueForecast, 
    usMapRender, 
    haversine, 
    calculate_top_suggestion
)
from .ml import hello

print(hello())

import os
from datetime import datetime
assets_path = os.path.join(os.path.dirname(__file__), "www")
os.makedirs(assets_path, exist_ok=True)

BASE_DIR = os.path.dirname(__file__)        # /cloud/project/app
DATA_DIR = os.path.join(BASE_DIR, "data")  # /cloud/project/app/data

# ----------------------------
# Sample Data for 10 States
# ----------------------------
data = [
    {"state": "California", "state_code": "CA", "zip_code": "90001", "income": 8, "cost_of_living": 7, "crime_rate": 4,
     "job_opportunities": 9, "climate": 8, "lat": 36.7783, "lon": -119.4179},
    {"state": "Texas", "state_code": "TX", "zip_code": "73301", "income": 7, "cost_of_living": 5, "crime_rate": 6,
     "job_opportunities": 8, "climate": 7, "lat": 31.9686, "lon": -99.9018},
    {"state": "New York", "state_code": "NY", "zip_code": "10001", "income": 9, "cost_of_living": 6, "crime_rate": 5,
     "job_opportunities": 9, "climate": 6, "lat": 42.1657, "lon": -74.9481},
    {"state": "Florida", "state_code": "FL", "zip_code": "33101", "income": 6, "cost_of_living": 6, "crime_rate": 7,
     "job_opportunities": 7, "climate": 9, "lat": 27.9944, "lon": -81.7603},
    {"state": "Illinois", "state_code": "IL", "zip_code": "60601", "income": 7, "cost_of_living": 5, "crime_rate": 6,
     "job_opportunities": 7, "climate": 6, "lat": 40.0, "lon": -89.0},
    {"state": "Pennsylvania", "state_code": "PA", "zip_code": "19101", "income": 7, "cost_of_living": 6,
     "crime_rate": 5,
     "job_opportunities": 7, "climate": 5, "lat": 41.2033, "lon": -77.1945},
    {"state": "Ohio", "state_code": "OH", "zip_code": "44101", "income": 6, "cost_of_living": 5, "crime_rate": 6,
     "job_opportunities": 7, "climate": 5, "lat": 40.3675, "lon": -82.9962},
    {"state": "Georgia", "state_code": "GA", "zip_code": "30301", "income": 7, "cost_of_living": 6, "crime_rate": 5,
     "job_opportunities": 7, "climate": 8, "lat": 32.1656, "lon": -82.9001},
    {"state": "North Carolina", "state_code": "NC", "zip_code": "27513", "income": 7, "cost_of_living": 6,
     "crime_rate": 5,
     "job_opportunities": 7, "climate": 7, "lat": 35.7596, "lon": -79.0193},
    {"state": "Michigan", "state_code": "MI", "zip_code": "48201", "income": 6, "cost_of_living": 5, "crime_rate": 7,
     "job_opportunities": 6, "climate": 4, "lat": 44.3148, "lon": -85.6024},
]

df = pd.DataFrame(data)

# ----------------------------
# Zip Code Lookup
# ----------------------------
zip_lookup = (
    pd.read_csv(os.path.join(DATA_DIR, "zipcodes_clean.csv"), dtype={"zip": "str"})
        .rename(columns={"lng": "lon"})[["zip", "lat", "lon"]]
        .set_index("zip")
        .to_dict(orient="index")
)

# ----------------------------
# UI
# ----------------------------
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
            :root {
                --primary-color: #4361ee;
                --secondary-color: #3f37c9;
                --bg-color: #f8f9fa;
                --card-bg: #ffffff;
                --text-color: #333333;
            }

            body {
                font-family: 'Roboto', 'Segoe UI', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                line-height: 1.6;
            }

            .app-header {
                background-color: var(--primary-color);
                color: white;
                padding: 15px 20px;
                margin-bottom: 25px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            .card {
                background-color: var(--card-bg);
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
                padding: 20px;
                margin-bottom: 20px;
                transition: transform 0.2s;
            }

            .card:hover {
                transform: translateY(-2px);
            }

            .btn-primary {
                background-color: var(--primary-color);
                border-color: var(--primary-color);
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: 500;
                transition: all 0.3s;
            }

            .btn-primary:hover {
                background-color: var(--secondary-color);
                border-color: var(--secondary-color);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }

            .form-control, .shiny-input-container {
                margin-bottom: 15px;
            }

            .input-label {
                font-weight: 500;
                margin-bottom: 6px;
                display: block;
            }

            .preference-slider .irs-bar {
                background-color: var(--primary-color);
            }

            .preference-slider .irs-handle {
                border-color: var(--primary-color);
            }

            #plot-container {
                position: relative;
            }

            .search-radius-control {
    position: absolute;
    top: 15%;
    right: 3%;
    # transform: translateX(-50%);
    z-index: 1000;
    background: white;
    padding: 5px;
    border-radius: 6px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    display: inline-block;
    min-width:50px;
    text-align: center;
}

            .info-box {
                height: 100%;
            }
            .map{
            height: 97%;
            }

            .info-card-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 12px;
                color: var(--primary-color);
            }

            .weight-description {
                font-size: 12px;
                color: #666;
                margin-top: -8px;
                margin-bottom: 12px;
            }
        """)
    ),
    # ui.head(
    #     ui.tags.link(rel="shortcut icon", href="favicon.ico")
    # ),
    # Header
    ui.div(
        ui.h2("US Relocation Recommendation Tool", class_="mb-0"),
        ui.p("Find your ideal location based on personalized preferences", class_="lead mb-0"),
        class_="app-header"
    ),

    # First row: Inputs and Map
    ui.row(
        # Left column - preference inputs
        ui.column(
            4,
            ui.output_ui('filter_container')

        ),

        # Right column - map
        ui.column(
            8,
            ui.output_ui("map_container")
        )
    ),

    # Second row: Charts and Info
    ui.row(
        # Left column - line chart
        ui.column(
            8,
            ui.output_ui('line_chart_container')

        ),

        # Right column - info box
        ui.column(
            4,
            ui.output_ui('information_container')

        )
    )
)


# ----------------------------
# Server Logic
# ----------------------------
def server(input, output, session):
    # Store inputs when submit is clicked
    selected_zip = reactive.Value("")
    selected_weights = reactive.Value({})
    computed_scores = reactive.Value(None)
    search_radius = reactive.Value("all")
    zoomed_figure = reactive.Value(None)

    @reactive.effect
    @reactive.event(input.submit)
    def update_values():
        print("Submit button clicked")

        # Update stored values when Submit is clicked
        selected_zip.set(input.zip_code().strip())  # Store entered zip code
        selected_weights.set({
            "w_income": input.weight_income(),
            "w_cost": input.weight_cost(),
            "w_crime": input.weight_crime(),
            "w_job": input.weight_job(),
            "w_climate": input.weight_climate()
        })
        compute_scores()

        # Reset to default radius when submitting new zip
        search_radius.set("all")

        # Update UI selector to match the default
        if checkZip(input.zip_code().strip()):
            ui.update_radio_buttons("search_radius", selected="all")

    @reactive.calc
    def compute_scores():

        # Compute scores only when submit is clicked
        weights = selected_weights.get()  # Get stored weights
        zip_code = selected_zip.get()  # Get stored zip code

        # Compute a base score as a weighted sum of the factors.
        df["base_score"] = (weights['w_income'] * df["income"] +
                            weights['w_cost'] * df["cost_of_living"] +
                            weights['w_crime'] * df["crime_rate"] +
                            weights['w_job'] * df["job_opportunities"] +
                            weights['w_climate'] * df["climate"])

        # Adjust scores based on proximity if a valid zip code is entered.
        # zip_code = input.zip_code().strip()
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
        computed_scores.set(df.copy())
        print("Final computed scores stored successfully!")

    @output
    @render_widget
    def us_map():
        scored_df = computed_scores.get()
        ## placeholder
        scored_df = pd.read_csv("./ml/sample_ML.csv",
                                dtype={"zip": "str"})  # <<< placeholder; will be replaced by ml predictions
        if scored_df is None or scored_df.empty:
            # Return a minimal empty figure instead of None
            empty_fig = go.Figure()
            empty_fig.update_layout(
                height=600,
                margin=dict(l=0, r=0, t=30, b=0),
                annotations=[dict(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )]
            )
            return go.FigureWidget(empty_fig)

        # Use withProgress to give the widget time to render
        with ui.Progress(min=0, max=1) as p:
            p.set(0.3, message="Generating map...")

            try:
                fig = usMapRender(scored_df)

                # Add a title that includes the current search radius
                radius = search_radius.get()
                if radius != "all":
                    title_text = f"US Regions Recommendation (Within {radius} km of {selected_zip.get()})"
                else:
                    title_text = "US Relocation Region Recommendation"

                fig.update_layout(
                    clickmode="event+select",
                    title_text=title_text,
                    height=600,
                    margin=dict(l=0, r=0, t=30, b=0)
                )

                p.set(0.7, message="Rendering widget...")
                widget = go.FigureWidget(fig)

                # Create a flag to track if we've handled the click already
                # This prevents processing the same click multiple times
                click_handled = False

                def handle_click(trace, points, selector):
                    # Use the nonlocal keyword to modify the flag
                    nonlocal click_handled

                    # If we've already handled this click, ignore it
                    if click_handled:
                        return

                    # If there are no points in this trace, ignore it
                    if not points.point_inds:
                        return

                    # We found a point! Mark the click as handled
                    click_handled = True

                    print(f"Click registered on trace {trace.name}!")
                    print(f"Point indices: {points.point_inds}")
                    idx = points.point_inds[0]

                    # Get the zip code from customdata
                    zipcode = trace.customdata[idx][0]
                    print(f"Selected zip code: {zipcode}")
                    selected_zip.set(zipcode)
                    # Update the ZIP code input field in the UI
                    ui.update_text("zip_code", value=zipcode)

                    # Reset the flag after a short delay to allow handling future clicks
                    # This is needed because all traces will fire their events at once
                    import threading
                    def reset_flag():
                        nonlocal click_handled
                        click_handled = False

                    threading.Timer(0.1, reset_flag).start()

                # def handle_hover(trace, points, selector):
                #     print("Hovering")
                #     # If there are no points in this trace, ignore it
                #     if not points.point_inds:
                #         return
                #     idx = points.point_inds[0]
                #     lat = trace.lat[idx]
                #     lon = trace.lon[idx]
                #     print(trace)
                #     zoom_fig = px.scatter_geo(
                #         pd.DataFrame([{"lat": lat, "lon": lon}]),
                #         lat="lat",
                #         lon="lon",
                #         opacity=0.6
                #     )
                #     zoom_fig.update_geos(
                #         center={"lat": lat, "lon": lon},
                #         projection_scale=10,
                #         visible=False,
                #     )
                #     zoom_fig.update_layout(
                #         margin=dict(l=0, r=0, t=0, b=0),
                #         height=250,
                #     )
                #
                #     zoomed_figure.set(zoom_fig)

                # Attach to all traces
                for i, trace in enumerate(widget.data):
                    trace.on_click(handle_click)
                    # trace.on_hover(handle_hover)

                p.set(1.0, message="Complete")
                return widget

            except Exception as e:
                print(f"Error generating map: {e}")
                # Return minimal figure on error
                empty_fig = go.Figure()
                empty_fig.update_layout(
                    height=600,
                    annotations=[dict(
                        text=f"Error generating map",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )]
                )
                return go.FigureWidget(empty_fig)

    @reactive.effect
    def monitor_us_map_click():
        print(f"us_map_click changed: {input['us_map_click']}")

    @output
    @render_widget
    def zoomed_map():
        fig = zoomed_figure.get()
        if fig is None:
            return None  # empty placeholder
        return go.FigureWidget(fig)

    @output
    @render.ui
    def search_radius_control():
        # Only show radio buttons if a zip code is selected
        if selected_zip.get() and checkZip(selected_zip.get()):
            return ui.div(
                ui.tags.h4("Search Radius:"),
                ui.input_radio_buttons(
                    "search_radius",
                    "",
                    {
                        "100": "Within 100 km",
                        "1000": "Within 1000 km",
                        "all": "All over USA"
                    },
                    selected=search_radius.get()
                )
            )
        else:
            return None

    @reactive.effect
    @reactive.event(input.search_radius)
    def update_search_radius():
        search_radius.set(input.search_radius())
        compute_scores()  # Recalculate scores with new radius
        print(f"Search radius updated to: {search_radius.get()}")
        calculate_suggestion_based_zipcode()

    def calculate_suggestion_based_zipcode():
        if search_radius.get() == '100':
            calculate_top_suggestion(selected_zip.get(), 100)
        elif search_radius.get() == '1000':
            calculate_top_suggestion(selected_zip.get(), 1000)

    @output
    @render.ui
    def map_container():
        scored_df = computed_scores.get()
        if scored_df is None or scored_df.empty:
            return None
        else:
            return ui.div(
                ui.h4("Location Recommendations", class_="mb-3"),
                ui.div(
                    output_widget("us_map"),
                    id="plot-container",
                    class_="mb-3"
                ),
                ui.div(
                    ui.output_ui("search_radius_control"),
                    class_="search-radius-control"
                ),
                # output_widget("zoomed_map"),

                class_="card map"
            )

    @output
    @render.ui
    def line_chart_container():
        if computed_scores.get() is None:
            return None
        if selected_zip.get() is '':
            return None
        else:
            return ui.div(
                ui.h4("Comparison Metrics", class_="mb-3"),
                ui.output_ui("line_chart"),
                class_="card"
            )

    @output
    @render.ui
    def information_container():
        if computed_scores.get() is None:
            return None
        if selected_zip.get() is '':
            return None
        else:
            return ui.div(
                ui.h4("Location Details", class_="mb-3"),
                ui.output_ui("info_box"),
                class_="card info-box"
            )

    @output
    @render.ui
    def filter_container():
        return ui.div(
            ui.h4("Your Preferences", class_="mb-4"),

            ui.div(
                ui.input_text(
                    "zip_code",
                    "Current ZIP Code",
                    placeholder="e.g., 10001",
                    width="100%"
                ),
                class_="mb-4"
            ),

            ui.p("Set importance weights for each factor (total: 100%)", class_="weight-description"),

            ui.div(
                ui.div(ui.strong("Income", class_="input-label")),
                ui.input_slider(
                    "weight_income",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider"
            ),

            ui.div(
                ui.div(ui.strong("Cost of Living", class_="input-label")),
                ui.input_slider(
                    "weight_cost",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider"
            ),

            ui.div(
                ui.div(ui.strong("Safety", class_="input-label")),
                ui.input_slider(
                    "weight_crime",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider"
            ),

            ui.div(
                ui.div(ui.strong("Job Opportunities", class_="input-label")),
                ui.input_slider(
                    "weight_job",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider"
            ),

            ui.div(
                ui.div(ui.strong("Climate", class_="input-label")),
                ui.input_slider(
                    "weight_climate",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider mb-4"
            ),

            ui.input_action_button(
                "submit",
                "Find My Ideal Locations",
                class_="btn-primary btn-lg w-100"
            ),

            class_="card"
        )

    @output
    @render.ui
    def line_chart():
        if computed_scores.get() is None:
            empty_fig = go.Figure()
            return ui.HTML(empty_fig.to_html(include_plotlyjs="cdn", full_html=True))
            # return ui.HTML("<p>Please click Submit to view trends.</p>")
        if selected_zip.get() is '':
            return None
        if not checkZip(selected_zip.get()):
            return ui.HTML("""
                        <div style="
                            background-color: #f8d7da;
                            color: #721c24;
                            padding: 15px;
                            border: 1px solid #f5c6cb;
                            border-radius: 5px;
                            text-align: center;
                            font-family: Arial, sans-serif;
                            font-size: 16px;
                            margin: 10px 0;
                        ">
                            <strong>Error:</strong> The ZIP code entered is not valid. Please enter a valid 5-digit  
                            ZIP code.
                        </div>
                    """)
        # Generate time series data
        df_trends = collectingLineGraphData(selected_zip.get())
        HomeValueForecast = collectingLineGraphData_HomeValueForecast(selected_zip.get())

        if (
                isinstance(HomeValueForecast, list)
                and len(HomeValueForecast) == 2
                and isinstance(HomeValueForecast[0], list)
                and len(HomeValueForecast[0]) > 0
                and isinstance(HomeValueForecast[1], (str, datetime.datetime, datetime.date))
        ):
            forcast = f"""Forecasted Home Value: <span style="color:#B3A369">{HomeValueForecast[0][0]['HomeValueForecast']:,.0f}</span> ({HomeValueForecast[1].strftime('%b')}, {HomeValueForecast[1].strftime('%Y')})"""
        else:
            forcast = ""

        if df_trends.empty:
            return ui.HTML("""
                                    <div style="
                                        background-color: #f8d7da;
                                        color: #721c24;
                                        padding: 15px;
                                        border: 1px solid #f5c6cb;
                                        border-radius: 5px;
                                        text-align: center;
                                        font-family: Arial, sans-serif;
                                        font-size: 16px;
                                        margin: 10px 0;
                                    ">
                                        <strong>Error:</strong> The ZIP code entered is not available.
                                    </div>
                                """)
        else:
            # Create figure with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Add Rentals to the primary y-axis
            fig.add_trace(
                go.Scatter(x=df_trends['date'], y=df_trends['Rentals'], name="Rentals", mode='lines+markers'),
                secondary_y=False,
            )

            # Add HomeValue to the secondary y-axis
            fig.add_trace(
                go.Scatter(x=df_trends['date'], y=df_trends['HomeValue'], name="Home Value", mode='lines+markers'),
                secondary_y=True,
            )

            # Add figure title and subtitle using annotations
            fig.update_layout(
                template='seaborn',
                title_text=f"""<b>Rentals vs Home Value</b> Over Time for: <span style="color:#B3A369; 
                font-weight:bold">{selected_zip.get()}</span>""",
                annotations=[
                    dict(
                        x=.95,
                        y=1.08,
                        xref='paper',
                        yref='paper',
                        text=forcast,
                        # text=f"""Forecasted Home Value: <span style="color:#B3A369">{HomeValueForecast[0][
                        # 'HomeValueForecast']:,.0f}</span> ({HomeValueForecast[1].strftime('%b')},
                        # {HomeValueForecast[1].strftime('%Y')})""",
                        showarrow=False,
                        font=dict(
                            size=12,
                            color="grey"
                        ),
                        align='center'
                    ),
                    dict(
                        x=0,
                        y=-0.3,
                        xref='paper',
                        yref='paper',
                        text="* Rentals & Home Value are on different scale",
                        showarrow=False,
                        font=dict(
                            size=12,
                            color="black"
                        ),
                        align='center'
                    )
                ],
                margin=dict(t=100),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )

            # Set x-axis title
            fig.update_xaxes(title_text="Date")

            # Set y-axes titles
            fig.update_yaxes(title_text="<b>Rentals</b>", secondary_y=False)
            fig.update_yaxes(title_text="<b>Home Value</b>", secondary_y=True)

            return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=True))

    @output
    @render.ui
    def info_box():
        if computed_scores.get() is None:
            return None
        if selected_zip.get() is '':
            return None
        if not checkZip(selected_zip.get()):
            return None
        info = collectingZipInformation(selected_zip.get())
        if len(info) == 0:
            return ui.HTML("""
                                                <div style="
                                                    background-color: #f8d7da;
                                                    color: #721c24;
                                                    padding: 15px;
                                                    border: 1px solid #f5c6cb;
                                                    border-radius: 5px;
                                                    text-align: center;
                                                    font-family: Arial, sans-serif;
                                                    font-size: 16px;
                                                    margin: 10px 0;
                                                ">
                                                    <strong>Error:</strong> The ZIP code entered is not avilable.
                                                </div>
                                            """)
        info_html = f"<h5>Additional Information for Zip Code: {selected_zip.get()}</h5><ul>"
        for key, value in info.items():
            info_html += f"<li><b>{key}:</b> {value}</li>"
        info_html += "</ul>"
        return ui.HTML(info_html)


# ----------------------------
# Create the Shiny App
# ----------------------------
app = App(app_ui, server, static_assets=assets_path)
