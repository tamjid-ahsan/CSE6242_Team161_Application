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
from .ml import predict_from_user_preference
# from utils import (
#     checkZip, 
#     collectingLineGraphData, 
#     collectingZipInformation,
#     collectingLineGraphData_HomeValueForecast, 
#     usMapRender, 
#     haversine, 
#     calculate_top_suggestion
# )
# from ml import predict_from_user_preference
import os
from datetime import datetime
assets_path = os.path.join(os.path.dirname(__file__), "www")
os.makedirs(assets_path, exist_ok=True)

BASE_DIR = os.path.dirname(__file__)            # /cloud/project/app
DATA_DIR = os.path.join(BASE_DIR, "data")       # /cloud/project/app/data

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
        ui.tags.link(rel="icon", type="image/x-icon", href="favicon.ico"),
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
            .filter-container {
    height: calc(100vh - 150px);
    overflow-y: auto;
    overflow-x: hidden;
    position: sticky;
    top: 20px;
    scrollbar-width: thin;
}
.filter-container::-webkit-scrollbar {
    width: 8px;
}

.filter-container::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.filter-container::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
}

.filter-container::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
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
            .preference-select select {
    padding: 8px;
    border-radius: 6px;
    border: 1px solid #ced4da;
    width: 100%;
    font-size: 14px;
}

.preference-select select:focus {
    border-color: var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.25);
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
            @media (max-width: 768px) {
    .filter-container {
        height: 500px;
        position: relative;
    }
        """)
    ),
    
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
    selected_preference = reactive.Value({})
    computed_scores = reactive.Value(None)
    search_radius = reactive.Value("all")
    zoomed_figure = reactive.Value(None)
    map_rendered = reactive.Value(False)
    # recomendation= reactive.Value(None)
    backupRecommendation = reactive.Value(None)

    @reactive.effect
    @reactive.event(input.submit)
    def update_values():
        print("Submit button clicked")

        # Update stored values when Submit is clicked
        selected_zip.set(input.zip_code().strip())  # Store entered zip code
        selected_weights.set({
            "w_climate": input.w_climate(),
            "w_education": input.w_education(),
            "w_health": input.w_health(),
            "w_cost": input.w_cost(),
            "w_politics": input.w_politics(),
            "w_density": input.w_density(),
        })
        selected_preference.set({
            "p_temp": input.p_temp(),
            "p_rain": input.p_rain(),
            "p_snow": input.p_snow(),
            "p_education": input.p_education(),
            "p_health": input.p_health(),
            "p_income": input.p_income(),
            "p_housing": input.p_housing(),
            "p_politics": input.p_politics(),
            "p_density": input.p_density(),
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
        preferences = selected_preference.get()
        print("##############################")
        print(weights)
        print(preferences)

        zip_code = selected_zip.get()  # Get stored zip code
        recommend_data = predict_from_user_preference(preferences, weights)
        backupRecommendation.set(recommend_data)
        print(recommend_data)
        print("##############################")
        computed_scores.set(recommend_data.copy())
        print("Final computed scores stored successfully!")

    @output
    @render_widget
    def us_map():
        scored_df = computed_scores.get()
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
            map_rendered.set(False)
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
                widget = go.FigureWidget(fig, skip_invalid=True)

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

                # Attach to all traces
                for i, trace in enumerate(widget.data):
                    trace.on_click(handle_click)
                    # trace.on_hover(handle_hover)

                p.set(1.0, message="Complete")
                map_rendered.set(True)
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

    @render.ui
    def info_label_ui():
        if map_rendered.get():
            return ui.div(ui.p("Put useful information"), id="info_label")
        else:
            return ui.div(id="info_label", style="display: none;")

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
            computed_scores.set(calculate_top_suggestion(selected_zip.get(), 100, backupRecommendation.get()))
        elif search_radius.get() == '1000':
            computed_scores.set(calculate_top_suggestion(selected_zip.get(), 1000, backupRecommendation.get()))
        else:
            computed_scores.set(backupRecommendation.get())

    @output
    @render.ui
    def map_container():
        scored_df = computed_scores.get()
        print(scored_df)
        if (scored_df is None or scored_df.empty) and (selected_zip.get() and checkZip(selected_zip.get())):
            return ui.div(
                ui.HTML("""
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
                                <strong>Notice:</strong> No recommendations found within the selected radius.
                            </div>
                        """),
                ui.div(
                    ui.output_ui("search_radius_control"),
                    class_="search-radius-control"
                ),
                class_="card map"
            )
        elif scored_df is None or scored_df.empty:
            return
        else:
            return ui.div(
                ui.h4("Location Recommendations", class_="mb-3"),
                ui.div(
                    output_widget("us_map"),
                    id="plot-container",
                    class_="mb-3"
                ),
                ui.div(
                    ui.output_ui("info_label_ui"),
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
                ui.h4("Comparison Metrics - Housing", class_="mb-3"),
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

    @render.ui
    def info_label_ui():
        if map_rendered.get():
            return ui.div(ui.p("Zoom using ➕/➖ or your scroll wheel, click ZIP codes for more info, and enter a ZIP plus set distance to limit your search radius."),
                          ui.p("Recommendations (Top 60) are ordered by rank, with Rank 1 (blue) being the highest ranking suggestion."),
                           id="info_label")
        else:
            return ui.div(id="info_label", style="display: none;")

    @output
    @render.ui
    def filter_container():
        return ui.div(
            ui.h4("Your Preferences", class_="mb-4"),
            # ui.p("Set importance weights for each factor (total: 100%)", class_="weight-description"),
            ui.div(
                ui.div(ui.strong("To what extent does ", ui.tags.b("weather"), " influence where you would like to live?", class_="input-label")),
                ui.input_slider(
                    "w_climate",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider mb-4"
            ),
            ui.div(
                ui.div(ui.strong("What kind of seasonal ", ui.tags.b("warmth or coolness"), " do you prefer?", class_="input-label")),
                ui.input_select(
                    "p_temp",
                    "",
                    choices={
                        "0": "I love warm, sunny weather",
                        "1": "I enjoy a nice balance — not too hot, not too cold",
                        "2": "I prefer cooler temperatures and winter vibes",
                        "3": "No preference"
                    },
                    selected="3",
                    width="100%"
                ),
                class_="preference-select mb-4"
            ),
            ui.div(
                ui.div(ui.strong("Would you enjoy a place that experiences frequent ", ui.tags.b("rain"), "?", class_="input-label")),
                ui.input_select(
                    "p_rain",
                    "",
                    choices={
                        "0": "I like places with lots of rain",
                        "1": "A little rain here and there is fine",
                        "2": "I'd rather avoid rainy weather",
                        "3": "No preference"
                    },
                    selected="3",
                    width="100%"
                ),
                class_="preference-select mb-4"
            ),
            ui.div(
                ui.div(ui.strong("How would you feel about having regular ", ui.tags.b("snowfall"), "?", class_="input-label")),
                ui.input_select(
                    "p_snow",
                    "",
                    choices={
                        "0": "I'd be happy with year-round winters",
                        "1": "I enjoy a snow day here and there",
                        "2": "I'd rather live somewhere snow-free",
                        "3": "No preference"
                    },
                    selected="3",
                    width="100%"
                ),
                class_="preference-select mb-4"
            ),
            ui.div(
                ui.div(ui.strong("How significant are local ", ui.tags.b("schools and universities")," in your move?",
                                 class_="input-label")),
                ui.input_slider(
                    "w_education",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider"
            ),
            ui.div(
                ui.div(ui.strong("Do you plan to engage with ", ui.tags.b("higher education")," where you move?", class_="input-label")),
                ui.input_select(
                    "p_education",
                    "",
                    choices={
                        "0": "Yes - I'd like to live in or near a college town",
                        "2": "No - I'd rather avoid areas centered around colleges",
                        "3": "No preference"
                    },
                    selected="2",
                    width="100%"
                ),
                class_="preference-select mb-4"
            ),
            ui.div(
                ui.div(
                    ui.strong("To what degree should ", ui.tags.b("community wellness"), " factor into your decision?", class_="input-label")),
                ui.input_slider(
                    "w_health",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider"
            ),
            ui.div(
                ui.div(ui.strong("How important is it that your community ", ui.tags.b("supports wellness activities"),"?", class_="input-label")),
                ui.input_select(
                    "p_health",
                    "",
                    choices={
                        "0": "Very important - I want to be in a health-conscious place",
                        "2": "I'm not into overly health-focused communities",
                        "3": "No preference"
                    },
                    selected="2",
                    width="100%"
                ),
                class_="preference-select mb-4"
            ),
            ui.div(
                ui.div(ui.strong("How much should ", ui.tags.b("affordability"), " influence your relocation?", class_="input-label")),
                ui.input_slider(
                    "w_cost",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider"
            ),
            ui.div(
                ui.div(ui.strong("What ", ui.tags.b("balance of expenses"), " feels right for your lifestyle?", class_="input-label")),
                ui.input_select(
                    "p_income",
                    "",
                    choices={
                        "0": "I'm okay with a higher cost if it comes with quality",
                        "1": "I'd like a good balance — not too cheap, not too pricey",
                        "2": "I want to keep expenses low and stretch my budget",
                        "3": "No preference"
                    },
                    selected="3",
                    width="100%"
                ),
                class_="preference-select mb-4"
            ),
            ui.div(
                ui.div(ui.strong("How important is ", ui.tags.b("finding affordable housing"), " in your search?", class_="input-label")),
                ui.input_select(
                    "p_housing",
                    "",
                    choices={
                        "0": "I'll pay more for the perfect place in the right location",
                        "1": "I want something nice, but within a reasonable budget",
                        "2": "I want affordable housing to save more",
                        "3": "No preference"
                    },
                    selected="3",
                    width="100%"
                ),
                class_="preference-select mb-4"
            ),
            ui.div(
                ui.div(ui.strong("How critical is the ", ui.tags.b("political atmosphere"), " in choosing a new home?", class_="input-label")),
                ui.input_slider(
                    "w_politics",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider"
            ),
            ui.div(
                ui.div(ui.strong("Which ", ui.tags.b("political environment"), " would you feel most comfortable in?", class_="input-label")),
                ui.input_select(
                    "p_politics",
                    "",
                    choices={
                        "0": "I'd prefer a more liberal or progressive area",
                        "1": "I'd like to live somewhere with a mix of political affiliations",
                        "2": "I'd prefer a more conservative community",
                        "3": "No preference"
                    },
                    selected="3",
                    width="100%"
                ),
                class_="preference-select mb-4"
            ),
            ui.div(
                ui.div(ui.strong(
                    "How important is ", ui.tags.b("living environment"), " (urban, suburban, rural) when deciding where to move?",
                    class_="input-label")),
                ui.input_slider(
                    "w_density",
                    "",
                    0, 1, 0.2,
                    step=0.1,
                    width="100%"
                ),
                class_="preference-slider"
            ),
            ui.div(
                ui.div(ui.strong("What ", ui.tags.b("size and vibe"), " of community best match your lifestyle?", class_="input-label")),
                ui.input_select(
                    "p_density",
                    "",
                    choices={
                        "0": "I want the energy and convenience of a city",
                        "1": "I'd prefer a smaller city or town with plenty to do but not too many people",
                        "2": "I want a quieter, nature-focused lifestyle",
                        "3": "No preference"
                    },
                    selected="3",
                    width="100%"
                ),
                class_="preference-select mb-4"
            ),
            ui.div(
                ui.input_text(
                    "zip_code",
                    ui.div(ui.strong("Current ZIP Code", class_="input-label")),
                    placeholder="e.g., 10001 (this is an optional input)",
                    width="100%"
                ),
                class_="mb-4"
            ),
            ui.input_action_button(
                "submit",
                "Find My Ideal Locations",
                class_="btn-primary btn-lg w-100"
            ),
            class_="card filter-container"
        )

    @output
    @render.ui
    def line_chart():
        try:
            print("Starting line_chart function")

            if computed_scores.get() is None:
                empty_fig = go.Figure()
                print("Returning empty figure")
                return ui.HTML(empty_fig.to_html(include_plotlyjs="cdn", full_html=True))

            if selected_zip.get() == '':
                print("No ZIP code selected")
                return None

            if not checkZip(selected_zip.get()):
                print(f"Invalid ZIP code: {selected_zip.get()}")
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

            print(f"Collecting data for ZIP: {selected_zip.get()}")

            # Pre-create a response for timeout or other issues
            error_response = ui.HTML("""
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
                            <strong>Error:</strong> Data processing took too long or encountered an error. 
                            Please try again with a different ZIP code.
                        </div>
                    """)

            # Collect data directly with better error handling
            try:
                print("Starting data collection")
                df_trends = collectingLineGraphData(selected_zip.get())
                print(f"Collected line graph data, rows: {len(df_trends) if not df_trends.empty else 0}")

                HomeValueForecast = collectingLineGraphData_HomeValueForecast(selected_zip.get())
                print("Collected home value forecast data")
                print(f"{HomeValueForecast = }")
            except Exception as e:
                print(f"Error during data collection: {e}")
                return ui.HTML(f"""
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
                                <strong>Error:</strong> Failed to collect data for ZIP code {selected_zip.get()}.
                                Details: {str(e)}
                            </div>
                        """)

            # Handle forecast display with proper error checking
            forecast = ""
            try:
                print("Processing forecast data")
                # if (isinstance(HomeValueForecast, list) and
                #         len(HomeValueForecast) == 2 and
                #         isinstance(HomeValueForecast[0], list) and
                #         len(HomeValueForecast[0]) > 0 and
                #         isinstance(HomeValueForecast[1], (str, datetime.datetime, datetime.date))):
                forecast = f"""Forecasted Home Value: <span style="color:#B3A369">{HomeValueForecast[0].get("HomeValueForecast"):,.0f}</span> ({HomeValueForecast[1].strftime('%b')}, {HomeValueForecast[1].strftime('%Y')})"""
                print("Generated forecast text")
                print(f"{forecast = }")
            except Exception as e:
                print(f"Error formatting forecast: {e}")
                # Continue without the forecast

            # Check if data is available
            if df_trends.empty:
                print("Empty dataframe returned")
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
                                <strong>Housing Data Unavailable:</strong> do not have housing information for this ZIP code.
                            </div>
                        """)

            # If df_trends is very large, sample it to reduce memory usage
            if len(df_trends) > 5000:
                print(f"Sampling large dataset: {len(df_trends)} records")
                df_trends = df_trends.sample(n=5000).sort_values('date')

            try:
                print("Creating plotly figure")
                # Create figure with secondary y-axis
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                print("Created subplot")

                # Add Rentals to the primary y-axis
                fig.add_trace(
                    go.Scatter(x=df_trends['date'], y=df_trends['Rentals'], name="Rentals", mode='lines+markers'),
                    secondary_y=False,
                )
                print("Added rentals trace")

                # Add HomeValue to the secondary y-axis
                fig.add_trace(
                    go.Scatter(x=df_trends['date'], y=df_trends['HomeValue'], name="Home Value", mode='lines+markers'),
                    secondary_y=True,
                )
                print("Added home value trace")

                # Add figure title and subtitle using annotations - create simpler layout first
                fig.update_layout(
                    template='seaborn',
                    title_text=f"""<b>Rentals vs Home Value</b> Over Time for: <span style="color:#B3A369; font-weight:bold">{selected_zip.get()}</span>""",
                    margin=dict(t=100),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )
                print("Updated basic layout")

                # Add annotations separately to isolate potential issues
                try:
                    fig.update_layout(
                        annotations=[
                            dict(
                                x=.95,
                                y=1.08,
                                xref='paper',
                                yref='paper',
                                text=forecast,
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
                        ]
                    )
                    print("Added annotations to figure")
                except Exception as e:
                    print(f"Error adding annotations: {e}")
                    # Continue without annotations

                # Set axes titles
                fig.update_xaxes(title_text="Date")
                fig.update_yaxes(title_text="Rentals", secondary_y=False)
                fig.update_yaxes(title_text="Home Value", secondary_y=True)
                print("Updated axes")

                print("Converting to HTML")
                # Generate HTML with size limit
                try:
                    # Use lower quality settings for plotly to reduce HTML size
                    html_content = fig.to_html(
                        include_plotlyjs="cdn",
                        full_html=True,
                        config={'responsive': True, 'displayModeBar': False}
                    )
                    print(f"Generated HTML content, size: {len(html_content)}")

                    if len(html_content) > 5000000: # 5MB limit
                        print(f"HTML content too large: {len(html_content)} bytes")
                        return ui.HTML("""
                                    <div style="
                                        background-color: #fff3cd;
                                        color: #856404;
                                        padding: 15px;
                                        border: 1px solid #ffeeba;
                                        border-radius: 5px;
                                        text-align: center;
                                        font-family: Arial, sans-serif;
                                        font-size: 16px;
                                        margin: 10px 0;
                                    ">
                                        <strong>Warning:</strong> Chart is too large to display. 
                                        Please try with a different ZIP code or date range.
                                    </div>
                                """)

                    print("Completed the line chart Now It will return")
                    return ui.HTML(html_content)
                except Exception as e:
                    print(f"Error generating HTML: {e}")
                    return error_response

            except Exception as e:
                print(f"Error creating chart: {e}")
                return ui.HTML(f"""
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
                                <strong>Error:</strong> Failed to create chart. Details: {str(e)}
                            </div>
                        """)

        except Exception as e:
            print(f"Unexpected error in line_chart: {e}")
            return ui.HTML(f"""
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
                            <strong>Error:</strong> An unexpected error occurred.
                        </div>
                    """)

    @output
    @render.ui
    def info_box():
        if computed_scores.get() is None:
            return None
        if selected_zip.get() == '':
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
                                                    <strong>Error:</strong> The ZIP code entered is not available.
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
