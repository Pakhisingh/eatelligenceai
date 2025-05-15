import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from nutrition_utils import load_nutrition_data
import streamlit as st
import warnings
import re
from difflib import SequenceMatcher
import os
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Suppress PyTorch warnings
warnings.filterwarnings('ignore', category=UserWarning)

class FoodRecognizer:
    def __init__(self):
        try:
            # Load the nutrition data
            self.df = load_nutrition_data()
            
            # Initialize the model (we'll use a pre-trained model)
            self.model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)
            self.model.eval()
            
            # Define image transformations
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            
            # Load ImageNet labels
            self.labels = self._load_imagenet_labels()
            
            # Load preset images
            self.preset_images = self._load_preset_images()
            
            # Map common food items to our dataset with variations
            self.food_mapping = {
                # Breakfast items
                'idli': ['idli', 'steamed rice cake', 'rice cake', 'rice dumpling', 'steamed cake', 'south indian breakfast'],
                'dosa': ['dosa', 'crepe', 'pancake', 'thin pancake', 'rice pancake', 'south indian crepe'],
                'upma': ['upma', 'semolina porridge', 'semolina dish', 'savory porridge', 'south indian breakfast'],
                'poha': ['poha', 'flattened rice', 'beaten rice', 'rice flakes', 'indian breakfast', 'rice dish'],
                'dhokla': ['dhokla', 'steamed cake', 'fermented cake', 'gram flour cake', 'gujarati snack'],
                
                # Breads and Rotis
                'roti': ['roti', 'chapati', 'flatbread', 'wheat bread', 'indian bread', 'whole wheat bread'],
                'naan': ['naan', 'leavened bread', 'tandoori bread', 'indian flatbread', 'bread'],
                'paratha': ['paratha', 'stuffed bread', 'layered bread', 'indian flatbread', 'bread'],
                'puri': ['puri', 'fried bread', 'deep fried bread', 'puffed bread', 'indian bread'],
                'kulcha': ['kulcha', 'leavened bread', 'stuffed bread', 'indian bread'],
                'bhatura': ['bhatura', 'fried bread', 'puffed bread', 'punjabi bread'],
                'thepla': ['thepla', 'flatbread', 'gujarati bread', 'spiced bread'],
                
                # Main dishes
                'sambar': ['sambar', 'lentil stew', 'vegetable stew', 'south indian stew', 'dal stew', 'soup'],
                'curry': ['curry', 'gravy', 'sauce', 'stew', 'masala', 'spiced dish', 'indian dish'],
                'rice': ['rice', 'biryani', 'pulao', 'fried rice', 'steamed rice', 'boiled rice', 'indian rice'],
                'dal': ['dal', 'lentil', 'lentil soup', 'pulse', 'legume', 'bean soup', 'indian dal'],
                'paneer': ['paneer', 'cottage cheese', 'cheese', 'indian cheese', 'fresh cheese', 'dairy'],
                'biryani': ['biryani', 'rice dish', 'spiced rice', 'indian rice dish', 'mixed rice'],
                'pulao': ['pulao', 'pilaf', 'rice pilaf', 'fried rice dish', 'indian rice'],
                
                # Snacks and Street Food
                'samosa': ['samosa', 'stuffed pastry', 'fried pastry', 'indian snack', 'savory pastry'],
                'pakora': ['pakora', 'fritter', 'bhajji', 'fried snack', 'vegetable fritter', 'indian snack'],
                'vada': ['vada', 'savory donut', 'lentil fritter', 'south indian snack', 'fried snack'],
                'bhel puri': ['bhel puri', 'puffed rice snack', 'chaat', 'indian street food', 'snack'],
                'pav bhaji': ['pav bhaji', 'bread and curry', 'vegetable curry', 'mumbai street food', 'snack'],
                'dabeli': ['dabeli', 'stuffed bun', 'gujarati snack', 'street food'],
                'vada pav': ['vada pav', 'burger', 'mumbai street food', 'potato fritter sandwich'],
                'dahi vada': ['dahi vada', 'yogurt fritter', 'lentil dumpling', 'south indian snack'],
                'ragda pattice': ['ragda pattice', 'potato patty', 'white peas curry', 'street food'],
                'sev puri': ['sev puri', 'crispy puri', 'chaat', 'street food'],
                'dahi puri': ['dahi puri', 'yogurt puri', 'chaat', 'street food'],
                'pani puri': ['pani puri', 'water puri', 'gol gappa', 'street food'],
                'kachori': ['kachori', 'stuffed pastry', 'fried snack', 'indian snack'],
                
                # Tikkas and Grilled Items
                'paneer tikka': ['paneer tikka', 'grilled cheese', 'tandoori cheese', 'indian appetizer'],
                'chicken tikka': ['chicken tikka', 'grilled chicken', 'tandoori chicken', 'indian appetizer'],
                'fish tikka': ['fish tikka', 'grilled fish', 'tandoori fish', 'indian appetizer'],
                
                # Curries and Gravies
                'paneer butter masala': ['paneer butter masala', 'butter paneer', 'paneer curry', 'indian curry'],
                'butter chicken': ['butter chicken', 'murgh makhani', 'chicken curry', 'indian curry'],
                'chicken curry': ['chicken curry', 'chicken masala', 'indian chicken dish'],
                'fish curry': ['fish curry', 'fish masala', 'indian fish dish'],
                'vegetable curry': ['vegetable curry', 'sabzi', 'indian vegetable dish'],
                'dal fry': ['dal fry', 'fried lentils', 'indian dal'],
                'dal makhani': ['dal makhani', 'black dal', 'punjabi dal'],
                'chana masala': ['chana masala', 'chickpea curry', 'chole', 'indian curry'],
                'rajma masala': ['rajma masala', 'kidney bean curry', 'indian curry'],
                'aloo matar': ['aloo matar', 'potato peas curry', 'indian curry'],
                'aloo gobi': ['aloo gobi', 'potato cauliflower curry', 'indian curry'],
                'baingan bharta': ['baingan bharta', 'eggplant curry', 'indian curry'],
                'jeera aloo': ['jeera aloo', 'cumin potatoes', 'indian curry'],
                'mushroom masala': ['mushroom masala', 'mushroom curry', 'indian curry'],
                'paneer bhurji': ['paneer bhurji', 'scrambled paneer', 'indian curry'],
                'egg curry': ['egg curry', 'anda curry', 'indian curry'],
                
                # Biryani Variations
                'hyderabadi biryani': ['hyderabadi biryani', 'spicy biryani', 'indian rice dish'],
                'lucknowi biryani': ['lucknowi biryani', 'awadhi biryani', 'indian rice dish'],
                'kolkata biryani': ['kolkata biryani', 'bengali biryani', 'indian rice dish'],
                'malabar biryani': ['malabar biryani', 'kerala biryani', 'indian rice dish'],
                'sindhi biryani': ['sindhi biryani', 'spicy biryani', 'indian rice dish'],
                'awadhi biryani': ['awadhi biryani', 'lucknowi biryani', 'indian rice dish'],
                'memoni biryani': ['memoni biryani', 'spicy biryani', 'indian rice dish'],
                'thalassery biryani': ['thalassery biryani', 'kerala biryani', 'indian rice dish'],
                'ambur biryani': ['ambur biryani', 'tamil biryani', 'indian rice dish'],
                'dindigul biryani': ['dindigul biryani', 'tamil biryani', 'indian rice dish'],
                'kalyani biryani': ['kalyani biryani', 'hyderabadi biryani', 'indian rice dish'],
                'beary biryani': ['beary biryani', 'mangalorean biryani', 'indian rice dish'],
                'bhatkali biryani': ['bhatkali biryani', 'konkani biryani', 'indian rice dish'],
                'kacchi biryani': ['kacchi biryani', 'raw biryani', 'indian rice dish'],
                'pakki biryani': ['pakki biryani', 'cooked biryani', 'indian rice dish'],
                'tehari biryani': ['tehari biryani', 'vegetable biryani', 'indian rice dish'],
                'kashmiri biryani': ['kashmiri biryani', 'mutton biryani', 'indian rice dish'],
                'mughlai biryani': ['mughlai biryani', 'royal biryani', 'indian rice dish'],
                'afghani biryani': ['afghani biryani', 'spicy biryani', 'indian rice dish'],
                'persian biryani': ['persian biryani', 'iranian biryani', 'indian rice dish'],
                'turkish biryani': ['turkish biryani', 'spicy biryani', 'indian rice dish'],
                'arabic biryani': ['arabic biryani', 'middle eastern biryani', 'indian rice dish'],
                
                # Common ingredients
                'potato': ['potato', 'aloo', 'spud', 'tuber', 'vegetable'],
                'tomato': ['tomato', 'tamatar', 'red fruit', 'vegetable'],
                'onion': ['onion', 'pyaz', 'bulb', 'vegetable'],
                'garlic': ['garlic', 'lehsun', 'clove', 'spice'],
                'ginger': ['ginger', 'adrak', 'root', 'spice'],
                'chili': ['chili', 'mirchi', 'pepper', 'spice'],
                'coriander': ['coriander', 'dhania', 'herb', 'green'],
                'cumin': ['cumin', 'jeera', 'seed', 'spice'],
                'turmeric': ['turmeric', 'haldi', 'spice', 'yellow'],
                'ghee': ['ghee', 'clarified butter', 'fat', 'oil']
            }
            
            # Create reverse mapping for easier lookup
            self.reverse_mapping = {}
            for key, variations in self.food_mapping.items():
                for variation in variations:
                    self.reverse_mapping[variation] = key
            
            # Create a list of all possible food names for similarity matching
            self.all_food_names = []
            for variations in self.food_mapping.values():
                self.all_food_names.extend(variations)
            
            # Create a DataFrame for faster lookup
            self.food_df = pd.DataFrame(self.df)
            
        except Exception as e:
            st.error(f"Error initializing food recognizer: {str(e)}")
            self.model = None
    
    def _load_imagenet_labels(self):
        """Load ImageNet labels"""
        try:
            import json
            import urllib
            url = 'https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json'
            response = urllib.request.urlopen(url)
            return json.loads(response.read())
        except Exception as e:
            st.error(f"Error loading ImageNet labels: {str(e)}")
            return []
    
    def _load_preset_images(self):
        """Load preset food images and their features"""
        preset_images = {}
        preset_dir = Path(__file__).parent / 'preset_images'
        
        if not preset_dir.exists():
            st.warning("Preset images directory not found. Creating directory...")
            preset_dir.mkdir(parents=True)
            return preset_images
        
        try:
            # Load each image in the preset directory
            for image_path in preset_dir.glob('*.jpg'):
                food_name = image_path.stem  # Get filename without extension
                try:
                    image = Image.open(image_path)
                    # Get image features
                    features = self._get_image_features(image)
                    preset_images[food_name] = {
                        'image': image,
                        'features': features
                    }
                except Exception as e:
                    st.warning(f"Error loading preset image {food_name}: {str(e)}")
            
            return preset_images
        except Exception as e:
            st.error(f"Error loading preset images: {str(e)}")
            return {}
    
    def _get_image_features(self, image: Image.Image) -> torch.Tensor:
        """Extract features from an image using the model"""
        try:
            # Preprocess the image
            img_tensor = self.transform(image).unsqueeze(0)
            
            # Get features
            with torch.no_grad():
                features = self.model(img_tensor)
                return features
        except Exception as e:
            st.error(f"Error extracting features: {str(e)}")
            return None
    
    def _compare_with_preset(self, image_features):
        """Compare uploaded image features with preset images."""
        if not self.preset_images:
            return None, 0.0
            
        # Ensure image_features is a 1D tensor
        if len(image_features.shape) > 1:
            image_features = image_features.flatten()
            
        best_match = None
        best_similarity = 0.0
        
        for food_name, preset_data in self.preset_images.items():
            preset_features = preset_data['features']
            
            # Ensure preset_features is a 1D tensor
            if len(preset_features.shape) > 1:
                preset_features = preset_features.flatten()
                
            # Calculate cosine similarity
            similarity = torch.nn.functional.cosine_similarity(
                image_features.unsqueeze(0),
                preset_features.unsqueeze(0),
                dim=1
            ).item()
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = food_name
                
        return best_match, best_similarity
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better matching"""
        return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    
    def _similarity_ratio(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, a, b).ratio()
    
    def _find_best_match(self, text: str) -> str:
        """Find the best matching food item from our dataset"""
        cleaned_text = self._clean_text(text)
        best_match = None
        best_score = 0.0
        
        # First try exact match in reverse mapping
        if cleaned_text in self.reverse_mapping:
            return self.reverse_mapping[cleaned_text]
        
        # Then try similarity matching
        for food_name in self.all_food_names:
            score = self._similarity_ratio(cleaned_text, food_name)
            if score > best_score and score > 0.6:  # Threshold for matching
                best_score = score
                best_match = food_name
        
        if best_match:
            return self.reverse_mapping[best_match]
        
        return None
    
    def recognize_food(self, image: Image.Image) -> str:
        """Recognize food from an image"""
        try:
            # First try matching with preset images
            image_features = self._get_image_features(image)
            if image_features is not None:
                preset_match, similarity = self._compare_with_preset(image_features)
                if preset_match and similarity > 0.7:  # High confidence threshold
                    return preset_match
            
            # If no preset match or low confidence, use model predictions
            img_tensor = self.transform(image).unsqueeze(0)
            
            with torch.no_grad():
                outputs = self.model(img_tensor)
                _, predicted = outputs.max(1)
                
                # Get the predicted label
                predicted_label = self.labels[predicted.item()]
                
                # Try to match the predicted label with our food items
                best_match = self._find_best_match(predicted_label)
                if best_match:
                    return best_match
                
                # If no match found, return the original prediction
                return predicted_label
                
        except Exception as e:
            st.error(f"Error recognizing food: {str(e)}")
            return None
    
    def get_nutrition_info(self, food_name: str) -> dict:
        """Get nutrition information for a food item"""
        try:
            # Clean the food name
            food_name = self._clean_text(food_name)
            
            # Try to find the food in our dataset
            food_data = self.food_df[self.food_df['Dish Name'].str.lower() == food_name]
            
            if not food_data.empty:
                return {
                    'name': food_data['Dish Name'].iloc[0],
                    'calories': food_data['Calories (kcal)'].iloc[0],
                    'protein': food_data['Protein (g)'].iloc[0],
                    'fats': food_data['Fats (g)'].iloc[0],
                    'carbohydrates': food_data['Carbohydrates (g)'].iloc[0]
                }
            
            # If not found, try fuzzy matching
            best_match = self._find_best_match(food_name)
            if best_match:
                food_data = self.food_df[self.food_df['Dish Name'].str.lower() == best_match]
                if not food_data.empty:
                    return {
                        'name': food_data['Dish Name'].iloc[0],
                        'calories': food_data['Calories (kcal)'].iloc[0],
                        'protein': food_data['Protein (g)'].iloc[0],
                        'fats': food_data['Fats (g)'].iloc[0],
                        'carbohydrates': food_data['Carbohydrates (g)'].iloc[0]
                    }
            
            return None
            
        except Exception as e:
            st.error(f"Error getting nutrition info: {str(e)}")
            return None
    
    def process_image(self, image: Image.Image) -> dict:
        """Process an image and return food recognition results"""
        try:
            # Recognize the food
            food_name = self.recognize_food(image)
            if not food_name:
                return None
            
            # Get nutrition information
            nutrition_info = self.get_nutrition_info(food_name)
            if not nutrition_info:
                return None
            
            return {
                'food_name': food_name,
                'nutrition_info': nutrition_info
            }
            
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return None 