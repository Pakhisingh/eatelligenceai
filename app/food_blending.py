import pandas as pd
import numpy as np
from nutrition_utils import load_nutrition_data
import random
from typing import List, Dict, Tuple

class FoodBlender:
    def __init__(self):
        self.df = load_nutrition_data()
        self._categorize_foods()
    
    def _categorize_foods(self):
        """Categorize foods based on their primary nutritional properties"""
        # Define categories based on nutritional properties
        self.categories = {
            'protein_rich': self.df[self.df['Protein'] > 10].copy(),
            'fiber_rich': self.df[self.df['Carbs'] > 20].copy(),  # Using carbs as proxy for fiber-rich foods
            'low_calorie': self.df[self.df['Calories'] < 100].copy(),
            'healthy_fats': self.df[self.df['Fat'] > 5].copy()
        }
        
        # Add some common Indian ingredients that might not be in the dataset
        self.common_ingredients = {
            'protein_rich': ['moong dal', 'chana dal', 'toor dal', 'urad dal', 'paneer', 'soy chunks'],
            'fiber_rich': ['oats', 'quinoa', 'bajra', 'jowar', 'ragi', 'brown rice'],
            'vegetables': ['spinach', 'beetroot', 'carrot', 'bottle gourd', 'bitter gourd', 'drumstick'],
            'healthy_fats': ['flaxseeds', 'chia seeds', 'walnuts', 'almonds', 'peanuts']
        }
    
    def _get_ingredient_from_category(self, category: str) -> str:
        """Get a random ingredient from a specific category"""
        if category in self.categories and not self.categories[category].empty:
            return random.choice(self.categories[category]['Food'].tolist())
        elif category in self.common_ingredients:
            return random.choice(self.common_ingredients[category])
        return None
    
    def suggest_combination(self, n_ingredients: int = 3) -> Dict:
        """
        Suggest a healthy food combination with nutritional information
        
        Args:
            n_ingredients (int): Number of ingredients to combine (default: 3)
            
        Returns:
            Dict containing:
            - combination: List of ingredients
            - nutritional_info: Dictionary with nutritional values
            - health_benefits: List of health benefits
        """
        # Define combination patterns
        patterns = [
            ['protein_rich', 'fiber_rich', 'vegetables'],
            ['protein_rich', 'fiber_rich', 'healthy_fats'],
            ['protein_rich', 'vegetables', 'healthy_fats']
        ]
        
        # Select a random pattern
        pattern = random.choice(patterns)
        
        # Get ingredients for the pattern
        ingredients = []
        for category in pattern:
            ingredient = self._get_ingredient_from_category(category)
            if ingredient:
                ingredients.append(ingredient)
        
        # Calculate nutritional information
        nutritional_info = self._calculate_nutritional_info(ingredients)
        
        # Generate health benefits
        health_benefits = self._generate_health_benefits(ingredients, nutritional_info)
        
        return {
            'combination': ' + '.join(ingredients),
            'nutritional_info': nutritional_info,
            'health_benefits': health_benefits
        }
    
    def _calculate_nutritional_info(self, ingredients: List[str]) -> Dict:
        """Calculate nutritional information for the combination"""
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        
        for ingredient in ingredients:
            # Try to find the ingredient in the dataset
            food_data = self.df[self.df['Food'].str.contains(ingredient, case=False, na=False)]
            if not food_data.empty:
                total_calories += food_data['Calories'].iloc[0]
                total_protein += food_data['Protein'].iloc[0]
                total_fat += food_data['Fat'].iloc[0]
                total_carbs += food_data['Carbs'].iloc[0]
            else:
                # Use estimated values for common ingredients
                if ingredient in self.common_ingredients['protein_rich']:
                    total_protein += 10  # Approximate protein content
                    total_calories += 100
                elif ingredient in self.common_ingredients['fiber_rich']:
                    total_carbs += 20
                    total_calories += 100
                elif ingredient in self.common_ingredients['vegetables']:
                    total_carbs += 5
                    total_calories += 30
                elif ingredient in self.common_ingredients['healthy_fats']:
                    total_fat += 5
                    total_calories += 50
        
        return {
            'calories': round(total_calories, 1),
            'protein': round(total_protein, 1),
            'fat': round(total_fat, 1),
            'carbs': round(total_carbs, 1)
        }
    
    def _generate_health_benefits(self, ingredients: List[str], nutritional_info: Dict) -> List[str]:
        """Generate health benefits based on ingredients and nutritional information"""
        benefits = []
        
        # Protein benefits
        if nutritional_info['protein'] > 15:
            benefits.append("High in protein - great for muscle building and repair")
        
        # Fiber benefits
        if nutritional_info['carbs'] > 20:
            benefits.append("Rich in fiber - promotes gut health and digestion")
        
        # Low calorie benefits
        if nutritional_info['calories'] < 300:
            benefits.append("Low calorie - suitable for weight management")
        
        # Healthy fats benefits
        if nutritional_info['fat'] > 5:
            benefits.append("Contains healthy fats - supports brain function and heart health")
        
        # Specific ingredient benefits
        if any(veg in ingredients for veg in self.common_ingredients['vegetables']):
            benefits.append("Packed with vitamins and minerals from fresh vegetables")
        
        if any(seed in ingredients for seed in ['flaxseeds', 'chia seeds']):
            benefits.append("Rich in omega-3 fatty acids - supports heart health")
        
        return benefits
