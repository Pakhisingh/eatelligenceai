import pandas as pd
import numpy as np
from nutrition_utils import load_nutrition_data
import streamlit as st

def get_healthier_alternatives(food_name: str, n_suggestions: int = 3) -> pd.DataFrame:
    """
    Suggest healthier alternatives for a given food item based on:
    1. Lower calories
    2. Higher protein-to-calories ratio
    
    Args:
        food_name (str): Name of the food item to find alternatives for
        n_suggestions (int): Number of alternatives to suggest (default: 3)
        
    Returns:
        pd.DataFrame: DataFrame containing the suggested alternatives with their nutrition info
    """
    try:
        # Load the nutrition data
        df = load_nutrition_data()
        
        # Find the target food
        target_food = df[df['Food'].str.contains(food_name, case=False, na=False)]
        
        if len(target_food) == 0:
            raise ValueError(f"No food found matching '{food_name}'")
        
        # Get the target food's nutrition values
        target_calories = target_food['Calories'].iloc[0]
        target_protein = target_food['Protein'].iloc[0]
        target_protein_ratio = target_protein / target_calories
        
        # Calculate protein ratio for all foods
        df['Protein_Ratio'] = df['Protein'] / df['Calories']
        
        # Filter for healthier alternatives:
        # 1. Lower calories than target
        # 2. Higher protein ratio than target
        alternatives = df[
            (df['Calories'] < target_calories) & 
            (df['Protein_Ratio'] > target_protein_ratio)
        ]
        
        # If we don't have enough alternatives, relax the criteria
        if len(alternatives) < n_suggestions:
            # Try with just lower calories
            alternatives = df[df['Calories'] < target_calories]
            
            # If still not enough, take the lowest calorie options
            if len(alternatives) < n_suggestions:
                alternatives = df.nsmallest(n_suggestions, 'Calories')
        
        # Sort by protein ratio and calories
        alternatives = alternatives.sort_values(
            by=['Protein_Ratio', 'Calories'],
            ascending=[False, True]
        ).head(n_suggestions)
        
        # Select and rename columns for the output
        result = alternatives[[
            'Food', 'Calories', 'Protein', 'Fat', 'Carbs', 'Protein_Ratio'
        ]].copy()
        
        # Add improvement metrics
        result['Calories_Reduction'] = target_calories - result['Calories']
        result['Protein_Ratio_Improvement'] = result['Protein_Ratio'] - target_protein_ratio
        
        # Format the output
        result = result.round(2)
        
        return result
    except Exception as e:
        st.error(f"Error finding healthier alternatives: {str(e)}")
        return pd.DataFrame()
