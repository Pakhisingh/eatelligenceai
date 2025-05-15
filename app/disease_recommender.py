import pandas as pd
import numpy as np
from nutrition_utils import load_nutrition_data
from typing import Dict, List, Tuple
import streamlit as st

class DiseaseRecommender:
    def __init__(self):
        try:
            self.df = load_nutrition_data()
            self._prepare_recommendations()
        except Exception as e:
            st.error(f"Error initializing disease recommender: {str(e)}")
            self.criteria = {}
            self.meal_types = {}
    
    def _prepare_recommendations(self):
        """Prepare disease-specific food recommendations"""
        try:
            # Define criteria for different conditions
            self.criteria = {
                'diabetes': {
                    'description': 'Low glycemic index foods with balanced macronutrients',
                    'filters': {
                        'Carbs': lambda x: x < 30,  # Lower carb content
                        'Protein': lambda x: x > 10,  # Higher protein
                        'Fat': lambda x: x < 15  # Moderate fat
                    }
                },
                'heart_disease': {
                    'description': 'Low sodium, low saturated fat foods with heart-healthy nutrients',
                    'filters': {
                        'Fat': lambda x: x < 10,  # Lower fat content
                        'Protein': lambda x: x > 8,  # Moderate protein
                        'Carbs': lambda x: x < 40  # Moderate carbs
                    }
                },
                'hypertension': {
                    'description': 'Low sodium, potassium-rich foods with balanced nutrients',
                    'filters': {
                        'Fat': lambda x: x < 12,  # Lower fat content
                        'Protein': lambda x: x > 8,  # Moderate protein
                        'Carbs': lambda x: x < 35  # Moderate carbs
                    }
                },
                'obesity': {
                    'description': 'Low calorie, high fiber foods with balanced macronutrients',
                    'filters': {
                        'Calories': lambda x: x < 200,  # Lower calorie content
                        'Protein': lambda x: x > 8,  # Higher protein
                        'Fat': lambda x: x < 10  # Lower fat
                    }
                },
                'pcos': {
                    'description': 'Low glycemic index, high fiber foods with balanced hormones',
                    'filters': {
                        'Carbs': lambda x: x < 25,  # Lower carb content
                        'Protein': lambda x: x > 12,  # Higher protein
                        'Fat': lambda x: x < 12  # Moderate fat
                    }
                },
                'thyroid': {
                    'description': 'Iodine-rich, selenium-containing foods with balanced nutrients',
                    'filters': {
                        'Protein': lambda x: x > 10,  # Higher protein
                        'Fat': lambda x: x < 15,  # Moderate fat
                        'Carbs': lambda x: x < 35  # Moderate carbs
                    }
                },
                'arthritis': {
                    'description': 'Anti-inflammatory foods with balanced nutrients',
                    'filters': {
                        'Fat': lambda x: x < 12,  # Lower fat content
                        'Protein': lambda x: x > 10,  # Higher protein
                        'Carbs': lambda x: x < 30  # Lower carbs
                    }
                }
            }
            
            # Define meal types and their recommended proportions
            self.meal_types = {
                'breakfast': 0.25,  # 25% of daily calories
                'lunch': 0.35,      # 35% of daily calories
                'dinner': 0.30,     # 30% of daily calories
                'snacks': 0.10      # 10% of daily calories
            }
        except Exception as e:
            st.error(f"Error preparing recommendations: {str(e)}")
            self.criteria = {}
            self.meal_types = {}
    
    def get_diet_plan(self, condition: str, daily_calories: int = 2000) -> Dict:
        """
        Generate a diet plan for a specific condition
        
        Args:
            condition (str): The condition (e.g., 'diabetes', 'heart_disease', etc.)
            daily_calories (int): Target daily calorie intake
            
        Returns:
            Dict containing:
            - description: Description of the diet plan
            - meals: Dictionary of meal recommendations
            - nutritional_summary: Summary of daily nutritional values
        """
        try:
            if not self.criteria or not self.meal_types:
                raise ValueError("Disease recommender not properly initialized")
                
            if condition not in self.criteria:
                raise ValueError(f"Unsupported condition: {condition}. Choose from: {list(self.criteria.keys())}")
            
            # Get the criteria for the condition
            criteria = self.criteria[condition]
            
            # Initialize the diet plan
            diet_plan = {
                'description': criteria['description'],
                'meals': {},
                'nutritional_summary': {
                    'calories': 0,
                    'protein': 0,
                    'fat': 0,
                    'carbs': 0
                }
            }
            
            # Get suitable foods for the condition
            suitable_foods = self.get_suitable_foods(condition)
            
            # Generate meal recommendations
            for meal_type, proportion in self.meal_types.items():
                meal_calories = daily_calories * proportion
                
                # If suitable_foods is still empty, fallback to full dataset
                if suitable_foods.empty:
                    st.warning(f"No foods available for {condition}. Showing random foods.")
                    meal_foods = self.df.sample(3)
                else:
                    meal_foods = suitable_foods.sample(min(3, len(suitable_foods)))
                
                # Calculate nutritional values
                meal_nutrition = {
                    'calories': meal_foods['Calories'].sum(),
                    'protein': meal_foods['Protein'].sum(),
                    'fat': meal_foods['Fat'].sum(),
                    'carbs': meal_foods['Carbs'].sum()
                }
                
                # Update the diet plan
                diet_plan['meals'][meal_type] = {
                    'foods': meal_foods['Food'].tolist(),
                    'nutrition': meal_nutrition
                }
                
                # Update the nutritional summary
                for nutrient in ['calories', 'protein', 'fat', 'carbs']:
                    diet_plan['nutritional_summary'][nutrient] += meal_nutrition[nutrient]
            
            return diet_plan
        except Exception as e:
            st.error(f"Error generating diet plan: {str(e)}")
            return {
                'description': f"Error: {str(e)}",
                'meals': {},
                'nutritional_summary': {
                    'calories': 0,
                    'protein': 0,
                    'fat': 0,
                    'carbs': 0
                }
            }
    
    def get_suitable_foods(self, condition: str) -> pd.DataFrame:
        """
        Get foods suitable for a specific condition
        
        Args:
            condition (str): The condition (e.g., 'diabetes', 'heart_disease', etc.)
            
        Returns:
            pd.DataFrame: DataFrame containing suitable foods
        """
        try:
            if not self.criteria:
                raise ValueError("Disease recommender not properly initialized")
                
            if condition not in self.criteria:
                raise ValueError(f"Unsupported condition: {condition}")
            
            # Get the criteria for the condition
            criteria = self.criteria[condition]
            
            # Apply filters to the dataset
            filtered_df = self.df.copy()
            for nutrient, filter_func in criteria['filters'].items():
                filtered_df = filtered_df[filtered_df[nutrient].apply(filter_func)]
            
            # Fallback: If no foods match, use the full dataset and show a warning
            if filtered_df.empty:
                st.warning(f"No foods matched the strict criteria for {condition}. Showing a general selection.")
                return self.df.copy()
            return filtered_df
        except Exception as e:
            st.error(f"Error getting suitable foods: {str(e)}")
            return self.df.copy()  # Fallback to full dataset 