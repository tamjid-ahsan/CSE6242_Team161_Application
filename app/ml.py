import numpy as np
import pandas as pd
import math
from sklearn.preprocessing import StandardScaler
import os

BASE_DIR = os.path.dirname(__file__)            # /cloud/project/app
DATA_DIR = os.path.join(BASE_DIR, "data")       # /cloud/project/app/data

# functions
def hello():
    return "Hello World"

def custom_rescale(series, new_max = 5):
    abs_values = series.abs()
    signs = np.sign(series)
    
    current_max = abs_values.max()
    
    rescaled_values = abs_values / current_max * new_max
    return rescaled_values * signs

def prefer_moderate(series):
    return custom_rescale(1/series.abs())
    
def prefer_low(series):
    return series * -1
    
def no_preference(series):
    return series.abs() * 0

def predict_from_user_preference(data_path:str=os.path.join(DATA_DIR, "cleaned_merged_data.csv")) -> pd.DataFrame: # './data/cleaned_merged_data.csv'
    """
    - Raw predictors are averaged within clusters and rescaled/standardized
    - Data is transformed based on user preferences (e.g., if user wants cold weather, avg_temp is multiplied by -1 to reverse the scale)
    - Best cluster is predicted by multiplying transformed feature values by user weights and summing across features - cluster with highest score is best cluster
    - Zip codes from the best cluster are isolated, data is rescaled/standardized
    - Same process for transforming zip code features based on user preferences + calculating final score (except for placeholder for handling user providing a zip code preference)
    - Final result is recommendation_data, which is data frame with geographic information, original feature variables, and overall score/rank; the top n zip codes can be pulled out
    TODO: show some aggregated info over city and state in case we want to show users what cities/states were the most aligned with their preferences

    Args:
        data_path (str, optional): _description_. Defaults to '../app/data/cleaned_merged_data.csv'.

    Returns:
        pd.DataFrame: _description_
    """
    full_data = pd.read_csv(data_path, dtype={'zip': 'string'})
    full_data['city'] = full_data['city'] + ", " + full_data['state_id']
    full_data = full_data.set_index('zip')
    
    # isolate prediction data - pulling back in raw feature columns, average by cluster, and restandardize + rescale
    raw_predictors = ['density', 'avg_temp', 'avg_snow', 'avg_rain', 'dem_lead', 'num_postsecondary_institutions', 
                    'health_rating', 'avg_salary_per_earner', 'recent_rental_price', 'recent_home_value']

    prediction_data = full_data[raw_predictors].copy()
    prediction_data['cluster_label'] = full_data['cluster_label']

    prediction_data = prediction_data.groupby('cluster_label').mean().reset_index()

    scaler = StandardScaler()
    prediction_data[raw_predictors] = scaler.fit_transform(prediction_data[raw_predictors])
    prediction_data[raw_predictors] = prediction_data[raw_predictors].apply(custom_rescale)

    # combine housing into one column based on average of rent + own
    prediction_data['housing_cost'] = prediction_data[['recent_rental_price', 'recent_home_value']].mean(axis = 1)
    prediction_data = prediction_data.drop(['recent_rental_price', 'recent_home_value'], axis = 1)
    
    first_prediction = prediction_data.copy()
    preference_mappings = {'p_temp': 'avg_temp', 'p_rain': 'avg_rain', 'p_snow': 'avg_snow', 'p_education': 'num_postsecondary_institutions', 'p_health': 'health_rating', 
                       'p_income': 'avg_salary_per_earner', 'p_housing': 'housing_cost', 'p_politics': 'dem_lead', 'p_density': 'density'}
    
    
    # test value #TODO: get data from front-end
    #-----------------------------------------------------------------------------------------------
    selected_preferences = {"p_temp": 0, "p_rain": 1, "p_snow": 3, "p_education": 3, "p_health": 0, 
                            "p_income": 2, "p_housing": 1, "p_politics": 0, "p_density": 1}

    selected_weights = {"w_climate": 1, "w_cost": 0.5, 'w_education': 0.1,
                        "w_health": 0.2, "w_politics": 0.4, "w_density": 0.8}
    #-----------------------------------------------------------------------------------------------
    
    # match transformation based on which answer is selected
    value_mappings = {1: prefer_moderate, 2: prefer_low, 3: no_preference}
    for value, method in value_mappings.items():
        # assuming selected_preferences.get() has been called and assigned to object preferences
        matching_inputs = [input_name for input_name, input_value in selected_preferences.items() if input_value == value]
    
    for input_name in matching_inputs:
        column = preference_mappings[input_name]
        first_prediction[column] = method(first_prediction[column])
        
    # calculate cluster scores based on values + identify best cluster

    # start with climate + cost variables since there are multiple feature components and average calculations will change if user doesn't have preference
    climate_vars = first_prediction[['avg_temp', 'avg_snow', 'avg_rain']]
    first_prediction['climate'] = climate_vars.drop(columns=climate_vars.columns[(climate_vars == 0).all()]).mean(axis = 1)

    cost_vars = first_prediction[['avg_salary_per_earner', 'housing_cost']]
    first_prediction['cost'] = cost_vars.drop(columns=cost_vars.columns[(cost_vars == 0).all()]).mean(axis = 1)

    # weight multiplier mappings
    weight_mappings = {"w_climate": 'climate', "w_cost": 'cost', 'w_education': 'num_postsecondary_institutions',
                    "w_health": 'health_rating', "w_politics": 'dem_lead', "w_density": 'density'}

    scores = pd.DataFrame()
    scores['cluster_label'] = first_prediction['cluster_label']

    for weight, column in weight_mappings.items():
        
        scores[weight.replace("w_", "") + "_score"] = first_prediction[column] * selected_weights[weight]
        
    scores['final_score'] = scores[['climate_score', 'cost_score', 'education_score', 'health_score', 'politics_score', 'density_score']].sum(axis = 1)

    best_cluster = scores.sort_values(by = 'final_score', ascending=False).reset_index()['cluster_label'][0]
    
    
    
    # now that user has been matched with a cluster, look within the cluster to determine which zip codes/cities/states/etc. are best match

    # isolate data from cluster zip codes and find best matches
    
    best_cluster_data = full_data[full_data['cluster_label'] == best_cluster].copy()

    second_prediction = best_cluster_data.copy()

    # re-standardize + scale the data so that we can see best options within the cluster
    second_prediction[raw_predictors] = scaler.fit_transform(second_prediction[raw_predictors])
    second_prediction[raw_predictors] = second_prediction[raw_predictors].apply(custom_rescale)

    # combine housing into one column based on average of rent + own
    second_prediction['housing_cost'] = second_prediction[['recent_rental_price', 'recent_home_value']].mean(axis = 1)
    second_prediction = second_prediction.drop(['recent_rental_price', 'recent_home_value'], axis = 1)

    for value, method in value_mappings.items():
        # assuming selected_preferences.get() has been called and assigned to object preferences
        matching_inputs = [input_name for input_name, input_value in selected_preferences.items() if input_value == value]
        
        for input_name in matching_inputs:
            column = preference_mappings[input_name]
            second_prediction[column] = method(second_prediction[column])

    climate_vars = second_prediction[['avg_temp', 'avg_snow', 'avg_rain']]
    second_prediction['climate'] = climate_vars.drop(columns=climate_vars.columns[(climate_vars == 0).all()]).mean(axis = 1)

    cost_vars = second_prediction[['avg_salary_per_earner', 'housing_cost']]
    second_prediction['cost'] = cost_vars.drop(columns=cost_vars.columns[(cost_vars == 0).all()]).mean(axis = 1)       
    
    scores = pd.DataFrame(index=second_prediction.index)

    for weight, column in weight_mappings.items():
        
        scores[weight.replace("w_", "") + "_score"] = second_prediction[column] * selected_weights[weight]

    scores['final_score'] = scores[['climate_score', 'cost_score', 'education_score', 'health_score', 'politics_score', 'density_score']].sum(axis = 1)
    
    
    
    best_zips = scores.sort_values(by = 'final_score', ascending=False).reset_index().copy()[['zip', 'final_score']]
    best_zips['rank'] = best_zips.index + 1

    recommendation_data = best_cluster_data[['lat', 'lng', 'city', 'state_name', 'population', 'density', 'avg_temp', 'avg_snow', 
                                            'avg_rain', 'dem_pct', 'rep_pct', 'num_postsecondary_institutions', 'health_rating', 
                                            'avg_salary_per_earner', 'recent_rental_price', 'recent_home_value']].copy().reset_index()

    recommendation_data = recommendation_data.merge(best_zips, on = 'zip').sort_values(by = 'rank').reset_index(drop=True)
    return recommendation_data