import openai
from typing import List, Dict
import os
from dotenv import load_dotenv
import json
import streamlit as st

# Try to load environment variables, but don't fail if .env file doesn't exist
try:
    load_dotenv()
except Exception as e:
    st.warning("Environment variables not loaded. Some features might be limited.")

class RecipeGenerator:
    def __init__(self):
        """Initialize the recipe generator with OpenAI client"""
        load_dotenv()
        try:
            api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = openai.OpenAI(api_key=api_key)
                self.is_api_available = True
            else:
                st.warning("OpenAI API key not found. Using fallback recipe generation.")
                self.is_api_available = False
                self.client = None
        except Exception as e:
            st.warning("Could not initialize OpenAI client. Using fallback recipe generation.")
            self.is_api_available = False
            self.client = None
        
        # Define common Indian ingredients
        self.ingredients = {
            'grains': [
                'ragi', 'bajra', 'jowar', 'quinoa', 'brown rice', 'red rice',
                'foxtail millet', 'little millet', 'kodo millet', 'barnyard millet'
            ],
            'pulses': [
                'moong dal', 'toor dal', 'chana dal', 'urad dal', 'masoor dal',
                'horse gram', 'black gram', 'green gram', 'red gram'
            ],
            'vegetables': [
                'palak', 'methi', 'lauki', 'tinda', 'karela', 'bhindi',
                'baingan', 'gajar', 'shimla mirch', 'tamatar'
            ],
            'spices': [
                'turmeric', 'cumin', 'coriander', 'mustard seeds', 'fenugreek',
                'asafoetida', 'curry leaves', 'cinnamon', 'cardamom', 'cloves'
            ],
            'healthy_fats': [
                'coconut oil', 'ghee', 'sesame oil', 'mustard oil', 'peanuts',
                'almonds', 'cashews', 'walnuts', 'flaxseeds', 'chia seeds'
            ]
        }
    
    def generate_recipe(self, ingredients: list, cuisine: str = "Indian") -> dict:
        """
        Generate a recipe based on available ingredients and cuisine type
        
        Args:
            ingredients (list): List of available ingredients
            cuisine (str): Type of cuisine (default: Indian)
            
        Returns:
            dict: Generated recipe with name, ingredients, instructions, and nutrition info
        """
        if not self.is_api_available:
            return self._get_fallback_recipe(ingredients, cuisine)
            
        try:
            prompt = f"""Generate a healthy {cuisine} recipe using these ingredients: {', '.join(ingredients)}.
            Include:
            1. Recipe name
            2. List of ingredients with quantities
            3. Step-by-step cooking instructions
            4. Nutritional information (calories, protein, carbs, fat)
            5. Health benefits
            Format the response as a JSON object with these keys: name, ingredients, instructions, nutrition, health_benefits"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional chef specializing in healthy cooking."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            try:
                recipe_text = response.choices[0].message.content
                recipe = json.loads(recipe_text)
                return recipe
            except (json.JSONDecodeError, AttributeError) as e:
                st.error("Error parsing recipe response. Using fallback recipe.")
                return self._get_fallback_recipe(ingredients, cuisine)
            
        except Exception as e:
            st.error(f"Error generating recipe. Using fallback recipe.")
            return self._get_fallback_recipe(ingredients, cuisine)
    
    def _get_fallback_recipe(self, ingredients: list, cuisine: str) -> dict:
        """Provide a fallback recipe when API is not available"""
        main_ingredient = ingredients[0] if ingredients else "mixed vegetables"
        
        fallback_recipes = {
            "Indian": {
                "name": f"{main_ingredient.title()} Curry",
                "ingredients": [
                    f"2 cups {main_ingredient}",
                    "1 onion, finely chopped",
                    "2 tomatoes, chopped",
                    "2 tbsp oil",
                    "1 tsp cumin seeds",
                    "1 tsp turmeric powder",
                    "1 tsp red chili powder",
                    "Salt to taste",
                    "Coriander leaves for garnish"
                ],
                "instructions": [
                    "1. Heat oil in a pan and add cumin seeds",
                    "2. Add chopped onions and sauté until golden brown",
                    "3. Add tomatoes and cook until soft",
                    "4. Add all spices and salt",
                    f"5. Add {main_ingredient} and cook until tender",
                    "6. Garnish with coriander leaves and serve hot"
                ],
                "nutrition": {
                    "calories": 150,
                    "protein": 4,
                    "carbs": 20,
                    "fat": 6
                },
                "health_benefits": [
                    "Rich in fiber",
                    "Low in calories",
                    "Good source of vitamins and minerals",
                    "Helps in weight management"
                ]
            }
        }
        
        return fallback_recipes.get(cuisine, fallback_recipes["Indian"])
    
    def get_ingredient_categories(self) -> Dict[str, List[str]]:
        """
        Get all available ingredient categories and their items
        
        Returns:
            Dict[str, List[str]]: Dictionary of ingredient categories and their items
        """
        return self.ingredients 