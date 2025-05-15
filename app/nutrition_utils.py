import pandas as pd
import numpy as np
import os
from pathlib import Path
import streamlit as st

def load_nutrition_data() -> pd.DataFrame:
    """
    Load and clean Indian food nutrition data from a CSV file.
    
    Returns:
        pd.DataFrame: Cleaned and standardized nutrition data
        
    The function:
    1. Loads the CSV file
    2. Removes rows with null values
    3. Standardizes columns: 'Calories', 'Protein', 'Fat', 'Carbs'
    4. Renames columns to match standard format
    """
    try:
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'Indian_Food_Nutrition_Processed.csv')
        
        # Load the data
        df = pd.read_csv(file_path)
        
        # Rename columns to standard format
        column_mapping = {
            'Dish Name': 'Food',
            'Calories (kcal)': 'Calories',
            'Protein (g)': 'Protein',
            'Fats (g)': 'Fat',
            'Carbohydrates (g)': 'Carbs'
        }
        df = df.rename(columns=column_mapping)
        
        # Select only the columns we need
        columns_to_keep = ['Food', 'Calories', 'Protein', 'Fat', 'Carbs']
        df = df[columns_to_keep]
        
        # Remove rows with null values
        df = df.dropna()
        
        # Convert numeric columns to float
        numeric_columns = ['Calories', 'Protein', 'Fat', 'Carbs']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove any rows that became NaN after conversion
        df = df.dropna(subset=numeric_columns)
        
        # Reset index after dropping rows
        df = df.reset_index(drop=True)
        
        return df
    except Exception as e:
        print(f"Error loading nutrition data: {str(e)}")
        # Return a basic DataFrame with some common Indian foods as fallback
        return pd.DataFrame({
            'Food': ['Idli', 'Dosa', 'Sambar', 'Upma', 'Poha'],
            'Calories': [39, 133, 90, 150, 250],
            'Protein': [1.9, 3.7, 4.5, 4.0, 6.0],
            'Fat': [0.2, 3.9, 2.0, 3.0, 2.0],
            'Carbs': [7.8, 22.0, 12.0, 25.0, 45.0]
        })

def get_nutrition_info(food_name: str) -> dict:
    """
    Get nutrition information for a specific food
    """
    try:
        df = load_nutrition_data()
        food_data = df[df['Food'].str.lower() == food_name.lower()]
        
        if not food_data.empty:
            return {
                'name': food_data['Food'].iloc[0],
                'calories': float(food_data['Calories'].iloc[0]),
                'protein': float(food_data['Protein'].iloc[0]),
                'fat': float(food_data['Fat'].iloc[0]),
                'carbs': float(food_data['Carbs'].iloc[0])
            }
        return None
    except Exception as e:
        st.error(f"Error getting nutrition info: {str(e)}")
        return None

def assess_health_impact(nutrition_info):
    """
    Assess the health impact of a food item based on its nutritional values.
    Returns a dictionary of health impacts and their descriptions.
    """
    impacts = {}
    
    # Calorie assessment
    calories = nutrition_info.get('calories', 0)
    if calories < 200:
        impacts['Calorie Content'] = "Low calorie content, good for weight management"
    elif calories < 400:
        impacts['Calorie Content'] = "Moderate calorie content, suitable for regular consumption"
    else:
        impacts['Calorie Content'] = "High calorie content, consume in moderation"
    
    # Protein assessment
    protein = nutrition_info.get('protein', 0)
    if protein > 15:
        impacts['Protein Content'] = "High protein content, good for muscle building and satiety"
    elif protein > 8:
        impacts['Protein Content'] = "Moderate protein content, contributes to daily protein needs"
    else:
        impacts['Protein Content'] = "Low protein content, consider pairing with protein-rich foods"
    
    # Fat assessment
    fat = nutrition_info.get('fat', 0)
    if fat < 5:
        impacts['Fat Content'] = "Low fat content, good for heart health"
    elif fat < 15:
        impacts['Fat Content'] = "Moderate fat content, provides essential fatty acids"
    else:
        impacts['Fat Content'] = "High fat content, consume in moderation"
    
    # Carbohydrate assessment
    carbs = nutrition_info.get('carbs', 0)
    if carbs < 20:
        impacts['Carbohydrate Content'] = "Low carbohydrate content, suitable for low-carb diets"
    elif carbs < 40:
        impacts['Carbohydrate Content'] = "Moderate carbohydrate content, provides energy"
    else:
        impacts['Carbohydrate Content'] = "High carbohydrate content, good for energy but monitor intake"
    
    # Overall health impact
    if calories < 300 and protein > 10 and fat < 10:
        impacts['Overall Health Impact'] = "Positive: This food is generally healthy and nutritious"
    elif calories < 500 and protein > 8 and fat < 15:
        impacts['Overall Health Impact'] = "Moderate: This food can be part of a balanced diet"
    else:
        impacts['Overall Health Impact'] = "Caution: Consume in moderation and balance with other foods"
    
    return impacts
