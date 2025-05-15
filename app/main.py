import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from nutrition_utils import load_nutrition_data, get_nutrition_info, assess_health_impact
from food_recognition import FoodRecognizer
from recipe_generator import RecipeGenerator
from disease_recommender import DiseaseRecommender
from healthy_alternatives import HealthyAlternatives
import json
import os

# Set page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="EATelligence AI",
    page_icon="🍛",
    layout="wide"
)

# Helper function for veg/non-veg filtering

def is_veg_food(food_name):
    nonveg_keywords = ['egg', 'chicken', 'fish', 'meat', 'mutton', 'prawn', 'beef', 'pork', 'lamb', 'turkey', 'duck', 'seafood']
    return not any(word in food_name.lower() for word in nonveg_keywords)

# Initialize components (models/utilities)
@st.cache_resource
def load_components():
    return {
        'nutrition_data': load_nutrition_data(),
        'food_recognizer': FoodRecognizer(),
        'recipe_generator': RecipeGenerator(),
        'disease_recommender': DiseaseRecommender(),
        'healthy_alternatives': HealthyAlternatives()
    }
components = load_components()

# Custom CSS for the entire app
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: #F0F7F0 !important;  /* Very light pastel green */
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)),
                    url('https://images.unsplash.com/photo-1498837167922-ddd27525d352?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
        background-size: cover;
        background-position: center;
        padding: 40px 20px;
        margin: -20px -20px 20px -20px;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-family: 'Comic Sans MS', 'Chalkboard SE', 'Marker Felt', cursive;
        color: #2E7D32;
        font-size: 2.8em;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        font-weight: bold;
        letter-spacing: 1px;
    }
    
    .header-subtitle {
        color: #666;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 20px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.9);
    }
    
    .sidebar-content {
        background-color: rgba(46, 125, 50, 0.1);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .sidebar-title {
        color: #2E7D32;
        font-size: 1.2em;
        margin-bottom: 10px;
    }
    
    /* Hide Streamlit warnings */
    .stDeployButton {
        display: none;
    }
    
    /* Hide secrets warning */
    .stAlert {
        display: none;
    }
    
    /* Content area styling */
    .main-content {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Remove white box from health impact */
    .health-impact {
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .custom-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 32px 18px 32px;
        background: #fff;
        border-radius: 0 0 18px 18px;
        box-shadow: 0 2px 8px rgba(46,125,50,0.07);
        margin-bottom: 0px;
        gap: 0px;
    }
    .navbar-logo {
        display: flex;
        align-items: center;
        font-weight: bold;
        font-size: 1.3em;
        color: #2E7D32;
        letter-spacing: 1px;
    }
    .navbar-links {
        display: flex;
        gap: 28px;
        align-items: center;
    }
    .navbar-link {
        color: #222;
        font-weight: 500;
        font-size: 1.08em;
        text-decoration: none;
        padding: 6px 18px;
        border-radius: 6px;
        transition: background 0.2s, color 0.2s;
        cursor: pointer;
    }
    .navbar-link.selected, .navbar-link:hover {
        background: #E8F5E9;
        color: #2E7D32;
    }
    .about-modal {
        background: #fff;
        border-radius: 12px;
        padding: 32px 24px;
        box-shadow: 0 4px 24px rgba(46,125,50,0.13);
        max-width: 420px;
        margin: 0 auto;
    }
    .about-title {
        color: #2E7D32;
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .about-desc {
        color: #444;
        font-size: 1.08em;
        margin-bottom: 18px;
    }
    /* Hero section alignment */
    .hero-row {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 380px;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    .hero-left, .hero-right {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Navigation state
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 'Food Analyzer'
if 'show_about' not in st.session_state:
    st.session_state['show_about'] = False

def set_tab(tab):
    st.session_state['active_tab'] = tab
    st.session_state['show_about'] = False

def show_about():
    st.session_state['show_about'] = True

def show_recipe_generator():
    st.subheader("AI-Based Food Innovation")
    st.write("Select a preset Indian dish to view its ingredients and health benefits.")
    preset_dishes = {
        "Ragi-Nutri Bar": {
            "ingredients": ["Ragi (Finger Millet)", "Jaggery", "Almonds", "Flaxseeds", "Curd"],
            "benefits": [
                "High in calcium & protein",
                "Natural sweeteners, rich in iron",
                "Omega-3 & fiber boost",
                "Probiotic benefits for gut health"
            ]
        },
        "Foxtail Moong Protein Dosa": {
            "ingredients": ["Foxtail millet", "Moong dal", "Chia seeds", "Curry leaves"],
            "benefits": [
                "Gluten-free, high in fiber",
                "Rich in plant-based protein",
                "Omega-3 & antioxidants",
                "Iron & digestive benefits"
            ]
        },
        "Makhana Beetroot Choco Shake": {
            "ingredients": ["Makhana (fox nuts)", "Dark cocoa", "Beetroot powder", "Dates", "Almonds"],
            "benefits": [
                "Low-calorie, high in calcium & protein",
                "Iron-rich, great for hemoglobin",
                "Antioxidants & heart health",
                "Natural sweetness & healthy fats"
            ]
        },
        "Quinoa Paneer Power Bowl": {
            "ingredients": ["Quinoa", "Paneer", "Spinach", "Turmeric", "Ginger"],
            "benefits": [
                "Complete protein, high in fiber",
                "Rich in calcium and protein",
                "Iron and vitamin K powerhouse",
                "Anti-inflammatory and digestive benefits"
            ]
        },
        "Bajra Berry Smoothie Bowl": {
            "ingredients": ["Bajra (Pearl Millet)", "Mixed Berries", "Yogurt", "Honey", "Chia Seeds"],
            "benefits": [
                "Rich in iron and magnesium",
                "Antioxidants and vitamin C",
                "Probiotics and protein",
                "Natural energy and omega-3"
            ]
        },
        "Jowar Methi Roti": {
            "ingredients": ["Jowar (Sorghum)", "Methi (Fenugreek)", "Ajwain", "Ghee", "Curd"],
            "benefits": [
                "Gluten-free, rich in fiber and minerals",
                "Blood sugar control, digestive aid",
                "Digestive health, anti-inflammatory",
                "Probiotics, protein source"
            ]
        },
        "Sprouted Moong Chaat": {
            "ingredients": ["Sprouted Moong", "Pomegranate", "Cucumber", "Mint", "Lemon"],
            "benefits": [
                "Enhanced protein and enzyme content",
                "Antioxidants and heart health",
                "Hydration and low calories",
                "Digestive aid and vitamin C"
            ]
        },
        "Oats Idli with Sambar": {
            "ingredients": ["Oats", "Urad Dal", "Vegetables", "Sambar Powder", "Coconut"],
            "benefits": [
                "Beta-glucan for heart health",
                "Complete protein source",
                "Fiber and micronutrients",
                "Digestive spices"
            ]
        },
        "Ragi Ladoo": {
            "ingredients": ["Ragi Flour", "Jaggery", "Dry Fruits", "Ghee", "Cardamom"],
            "benefits": [
                "Calcium and iron rich",
                "Natural sweetener with minerals",
                "Healthy fats and protein",
                "Digestive aid"
            ]
        },
        "Bajra Khichdi": {
            "ingredients": ["Bajra", "Moong Dal", "Vegetables", "Ghee", "Spices"],
            "benefits": [
                "Rich in iron and magnesium",
                "Easy to digest protein",
                "Fiber and vitamins",
                "Digestive and anti-inflammatory"
            ]
        }
    }
    dish_names = list(preset_dishes.keys())
    selected_dish = st.selectbox("Select a dish", dish_names)
    if selected_dish:
        st.markdown(f"#### Ingredients for {selected_dish}:")
        for ingredient in preset_dishes[selected_dish]["ingredients"]:
            st.write(f"- {ingredient}")
        st.markdown(f"#### Health Benefits:")
        for benefit in preset_dishes[selected_dish]["benefits"]:
            st.write(f"- {benefit}")

# Custom Navbar with Streamlit event handling
nav1, nav2, nav3, nav4, nav5, _ = st.columns([1.5, 2, 2.2, 2.2, 1.7, 7])
with nav1:
    st.markdown("<div class='navbar-logo'><span>🟢</span> <span>Eatelligence AI</span></div>", unsafe_allow_html=True)
with nav2:
    if st.button('Food Analyzer', key='nav_food', help='Go to Food Analyzer'):
        st.session_state['active_tab'] = 'Food Analyzer'
        st.session_state['show_about'] = False
with nav3:
    if st.button('AI-Based Food Innovation', key='nav_innov', help='Go to AI-Based Food Innovation'):
        st.session_state['active_tab'] = 'AI-Based Food Innovation'
        st.session_state['show_about'] = False
with nav4:
    if st.button('Disease-Specific Diets', key='nav_disease', help='Go to Disease-Specific Diets'):
        st.session_state['active_tab'] = 'Disease-Specific Diets'
        st.session_state['show_about'] = False
with nav5:
    if st.button('Healthier Alternatives', key='nav_alt', help='Go to Healthier Alternatives'):
        st.session_state['active_tab'] = 'Healthier Alternatives'
        st.session_state['show_about'] = False
with _:
    if st.button('ABOUT', key='nav_about', help='About the project'):
        st.session_state['show_about'] = True

# Main Hero Section
if st.session_state['active_tab'] == 'Food Analyzer' and not st.session_state['show_about']:
    st.markdown("""
    <div class='hero-row'>
        <div class='hero-left' style='flex:1.1; padding-right: 32px;'>
            <div style='color: #2E7D32; font-weight: 600; font-size: 1.1em; margin-bottom: 10px;'>AI-Powered Food Analysis</div>
            <div style='font-size: 2.7em; font-weight: bold; color: #222; line-height: 1.13; margin-bottom: 10px;'>
                Discover the <span style='color: #2E7D32;'>Nutritional Secrets</span><br>of Your Food
            </div>
            <div style='color: #444; font-size: 1.18em; margin-bottom: 30px;'>
                Upload food images and get instant AI analysis of nutritional content, ingredients, and health insights. Make smarter food choices with Eatelligence.
            </div>
        </div>
        <div class='hero-right' style='flex:1; padding-left: 32px;'>
            <div style='background: #fff; border-radius: 18px; box-shadow: 0 2px 12px rgba(46,125,50,0.09); padding: 24px 18px 18px 18px;'>
                <img src='https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80' style='width:100%; border-radius: 12px; margin-bottom: 18px;' alt='Healthy Food'/>
                <div style='font-weight: 600; color: #2E7D32; font-size: 1.13em; margin-bottom: 8px;'>Nutritional Analysis</div>
                <div style='display: flex; gap: 18px; margin-bottom: 8px;'>
                    <div style='background: #E8F5E9; border-radius: 8px; padding: 10px 18px; min-width: 80px; text-align: center;'>
                        <div style='color: #2E7D32; font-size: 1.2em; font-weight: bold;'>320</div>
                        <div style='color: #444; font-size: 0.98em;'>Calories</div>
                    </div>
                    <div style='background: #E8F5E9; border-radius: 8px; padding: 10px 18px; min-width: 80px; text-align: center;'>
                        <div style='color: #2E7D32; font-size: 1.2em; font-weight: bold;'>18g</div>
                        <div style='color: #444; font-size: 0.98em;'>Protein</div>
                    </div>
                    <div style='background: #E8F5E9; border-radius: 8px; padding: 10px 18px; min-width: 80px; text-align: center;'>
                        <div style='color: #2E7D32; font-size: 1.2em; font-weight: bold;'>42g</div>
                        <div style='color: #444; font-size: 0.98em;'>Carbs</div>
                    </div>
                </div>
                <div style='color: #2E7D32; font-weight: 500; margin-top: 8px;'>Health Score <span style='float:right;'>Excellent</span></div>
                <div style='background: #E8F5E9; height: 8px; border-radius: 6px; margin-top: 4px;'><div style='background: #2E7D32; width: 90%; height: 100%; border-radius: 6px;'></div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ABOUT Modal/Section
if st.session_state['show_about']:
    st.markdown("""
    <div class='about-modal'>
        <div class='about-title'>About Eatelligence AI</div>
        <div class='about-desc'>
            <b>Developers:</b> Pakhi Singh Tak, Ilansha Singh Sisodia<br><br>
            <b>Project Brief:</b> EATelligence AI is an AI-powered food analyzer and recommendation system designed to promote healthy eating habits. The app enables users to analyze nutritional content in real-time, receive healthier food alternatives, and explore AI-driven innovative food blends using traditional Indian ingredients. It also offers personalized meal suggestions tailored to common lifestyle diseases, helping users make informed and balanced dietary choices.<br><br>
            <span style='color:#2E7D32;'>This project has been developed as part of a B.Tech Final Year Project.</span>
        </div>
        <div style='text-align:center; margin-top:18px;'>
            <button onclick="window.location.hash='food-analyzer';window.dispatchEvent(new Event('hashchange'))" style='background:#2E7D32;color:#fff;border:none;padding:8px 22px;border-radius:6px;font-size:1em;cursor:pointer;'>Close</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Tab switching logic
if not st.session_state['show_about']:
    if st.session_state['active_tab'] == 'Food Analyzer':
        # Hero section (already shown above)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### 📸 Upload Food Image")
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Food Image", use_column_width=True)
                food_name = components['food_recognizer'].recognize_food(image)
                if food_name:
                    st.success(f"Recognized Food: {food_name}")
                    nutrition_info = get_nutrition_info(food_name)
                    if nutrition_info:
                        st.markdown("### 📊 Nutritional Information")
                        nutrition_df = pd.DataFrame([nutrition_info])
                        st.markdown('<div class="nutrition-table">', unsafe_allow_html=True)
                        st.dataframe(nutrition_df, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        macronutrients = pd.DataFrame({
                            'Nutrient': ['Protein', 'Fat', 'Carbohydrates'],
                            'Amount': [nutrition_info['protein'], nutrition_info['fat'], nutrition_info['carbs']]
                        })
                        fig = px.pie(
                            macronutrients,
                            values='Amount',
                            names='Nutrient',
                            title="Macronutrient Distribution",
                            color_discrete_sequence=['#2E7D32', '#81C784', '#A5D6A7'],
                            hole=0.4
                        )
                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            insidetextfont=dict(size=14, color='white'),
                            marker=dict(line=dict(color='white', width=2))
                        )
                        fig.update_layout(
                            title_x=0.5,
                            title_font_size=20,
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown("### 🏥 Health Impact Assessment")
                        health_impact = assess_health_impact(nutrition_info)
                        for impact, details in health_impact.items():
                            impact_class = "positive" if "positive" in details.lower() else "caution" if "moderate" in details.lower() else "negative"
                            st.markdown(f"<div class='impact-item {impact_class}'><h4 style='margin: 0;'>{impact}</h4><p style='margin: 5px 0;'>{details}</p></div>", unsafe_allow_html=True)
                    else:
                        st.warning("Nutritional information not available for this food item.")
                else:
                    st.error("Could not recognize the food in the image. Please try another image or use text input.")
        with col2:
            st.markdown("### 🔍 Search by Name")
            food_name = st.text_input("Enter food name")
            if food_name:
                nutrition_info = get_nutrition_info(food_name)
                if nutrition_info:
                    st.markdown("### 📊 Nutritional Information")
                    nutrition_df = pd.DataFrame([nutrition_info])
                    st.markdown('<div class="nutrition-table">', unsafe_allow_html=True)
                    st.dataframe(nutrition_df, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    macronutrients = pd.DataFrame({
                        'Nutrient': ['Protein', 'Fat', 'Carbohydrates'],
                        'Amount': [nutrition_info['protein'], nutrition_info['fat'], nutrition_info['carbs']]
                    })
                    fig = px.pie(
                        macronutrients,
                        values='Amount',
                        names='Nutrient',
                        title="Macronutrient Distribution",
                        color_discrete_sequence=['#2E7D32', '#81C784', '#A5D6A7'],
                        hole=0.4
                    )
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        insidetextfont=dict(size=14, color='white'),
                        marker=dict(line=dict(color='white', width=2))
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_size=20,
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("### 🏥 Health Impact Assessment")
                    health_impact = assess_health_impact(nutrition_info)
                    for impact, details in health_impact.items():
                        impact_class = "positive" if "positive" in details.lower() else "caution" if "moderate" in details.lower() else "negative"
                        st.markdown(f"<div class='impact-item {impact_class}'><h4 style='margin: 0;'>{impact}</h4><p style='margin: 5px 0;'>{details}</p></div>", unsafe_allow_html=True)
                else:
                    st.warning("Nutritional information not available for this food item.")
    elif st.session_state['active_tab'] == 'AI-Based Food Innovation':
        show_recipe_generator()
    elif st.session_state['active_tab'] == 'Disease-Specific Diets':
        st.subheader("🩺 Disease-Specific Diets")
        veg_option = st.radio("Choose Diet Type:", ["Veg", "Non-Veg"], horizontal=True)
        diseases = ["diabetes", "heart_disease", "hypertension", "obesity", "pcos", "thyroid", "arthritis"]
        disease_names = {
            "diabetes": "Diabetes",
            "heart_disease": "Heart Disease",
            "hypertension": "Hypertension",
            "obesity": "Obesity",
            "pcos": "PCOS",
            "thyroid": "Thyroid Disorders",
            "arthritis": "Arthritis"
        }
        selected_disease = st.selectbox("Select a health condition", diseases, format_func=lambda x: disease_names[x])
        daily_calories = st.slider("Daily Calorie Target", min_value=1200, max_value=3000, value=2000, step=100)

        # Load the new CSV for this module only
        disease_df = pd.read_csv(os.path.join("app", "indian_disease_diet_nutrition.csv"))

        class DiseaseRecommenderCustom:
            def __init__(self, df):
                self.df = df
                self.criteria = {
                    'diabetes': {'description': 'Low glycemic index foods with balanced macronutrients', 'filters': {'Carbs': lambda x: x < 30, 'Protein': lambda x: x > 6, 'Fat': lambda x: x < 15}},
                    'heart_disease': {'description': 'Low sodium, low saturated fat foods with heart-healthy nutrients', 'filters': {'Fat': lambda x: x < 10, 'Protein': lambda x: x > 6, 'Carbs': lambda x: x < 40}},
                    'hypertension': {'description': 'Low sodium, potassium-rich foods with balanced nutrients', 'filters': {'Fat': lambda x: x < 12, 'Protein': lambda x: x > 6, 'Carbs': lambda x: x < 35}},
                    'obesity': {'description': 'Low calorie, high fiber foods with balanced macronutrients', 'filters': {'Calories': lambda x: x < 200, 'Protein': lambda x: x > 6, 'Fat': lambda x: x < 10}},
                    'pcos': {'description': 'Low glycemic index, high fiber foods with balanced hormones', 'filters': {'Carbs': lambda x: x < 25, 'Protein': lambda x: x > 8, 'Fat': lambda x: x < 12}},
                    'thyroid': {'description': 'Iodine-rich, selenium-containing foods with balanced nutrients', 'filters': {'Protein': lambda x: x > 8, 'Fat': lambda x: x < 15, 'Carbs': lambda x: x < 35}},
                    'arthritis': {'description': 'Anti-inflammatory foods with balanced nutrients', 'filters': {'Fat': lambda x: x < 12, 'Protein': lambda x: x > 8, 'Carbs': lambda x: x < 30}}
                }
                self.meal_types = {'breakfast': 0.25, 'lunch': 0.35, 'dinner': 0.30, 'snacks': 0.10}
            def get_diet_plan(self, condition, daily_calories=2000):
                if condition not in self.criteria:
                    return None
                criteria = self.criteria[condition]
                diet_plan = {'description': criteria['description'], 'meals': {}, 'nutritional_summary': {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}}
                suitable_foods = self.get_suitable_foods(condition)
                for meal_type, proportion in self.meal_types.items():
                    meal_calories = daily_calories * proportion
                    if suitable_foods.empty:
                        meal_foods = self.df.sample(3)
                    else:
                        meal_foods = suitable_foods.sample(min(3, len(suitable_foods)))
                    meal_nutrition = {
                        'calories': meal_foods['Calories'].sum(),
                        'protein': meal_foods['Protein'].sum(),
                        'fat': meal_foods['Fat'].sum(),
                        'carbs': meal_foods['Carbs'].sum()
                    }
                    diet_plan['meals'][meal_type] = {'foods': meal_foods['Food'].tolist(), 'nutrition': meal_nutrition}
                    for nutrient in ['calories', 'protein', 'fat', 'carbs']:
                        diet_plan['nutritional_summary'][nutrient] += meal_nutrition[nutrient]
                return diet_plan
            def get_suitable_foods(self, condition):
                if condition not in self.criteria:
                    return self.df.copy()
                criteria = self.criteria[condition]
                filtered_df = self.df.copy()
                for nutrient, filter_func in criteria['filters'].items():
                    filtered_df = filtered_df[filtered_df[nutrient].apply(filter_func)]
                if filtered_df.empty:
                    return self.df.copy()
                return filtered_df
        disease_recommender_custom = DiseaseRecommenderCustom(disease_df)

        if st.button("Generate Diet Plan"):
            diet_plan = disease_recommender_custom.get_diet_plan(selected_disease, daily_calories)
            if diet_plan and 'description' in diet_plan:
                st.subheader(f"Diet Plan for {disease_names[selected_disease]}")
                st.info(diet_plan['description'])
                st.subheader("Daily Meal Plan")
                for meal_type, meal_info in diet_plan['meals'].items():
                    # Filter foods by veg/non-veg
                    if veg_option == "Veg":
                        foods = [f for f in meal_info['foods'] if is_veg_food(f)]
                    else:
                        foods = meal_info['foods']
                    with st.expander(f"{meal_type.title()} ({int(daily_calories * disease_recommender_custom.meal_types[meal_type])} calories)"):
                        st.write("Foods:")
                        for food in foods:
                            st.write(f"- {food}")
                        st.write("Nutritional Information:")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Calories", f"{meal_info['nutrition']['calories']:.0f}")
                        with col2:
                            st.metric("Protein", f"{meal_info['nutrition']['protein']:.1f}g")
                        with col3:
                            st.metric("Fat", f"{meal_info['nutrition']['fat']:.1f}g")
                        with col4:
                            st.metric("Carbs", f"{meal_info['nutrition']['carbs']:.1f}g")
                st.subheader("Daily Nutritional Summary")
                summary = diet_plan['nutritional_summary']
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Calories", f"{summary['calories']:.0f}")
                with col2:
                    st.metric("Total Protein", f"{summary['protein']:.1f}g")
                with col3:
                    st.metric("Total Fat", f"{summary['fat']:.1f}g")
                with col4:
                    st.metric("Total Carbs", f"{summary['carbs']:.1f}g")
                st.subheader("Suitable Foods")
                suitable_foods = disease_recommender_custom.get_suitable_foods(selected_disease)
                if veg_option == "Veg":
                    suitable_foods = suitable_foods[suitable_foods['Food'].apply(is_veg_food)]
                st.dataframe(suitable_foods[['Food', 'Calories', 'Protein', 'Fat', 'Carbs']])
            else:
                st.error("Could not generate diet plan. Please try again.")
    elif st.session_state['active_tab'] == 'Healthier Alternatives':
        st.subheader("🥗 Healthier Alternatives")
        food_name = st.text_input("Enter a food item to find healthier alternatives")
        if food_name:
            alternatives = components['healthy_alternatives'].get_alternatives(food_name)
            if alternatives is not None:
                if isinstance(alternatives, list):
                    if not alternatives:
                        st.error("Could not find healthier alternatives for this food.")
                    else:
                        alternatives_df = pd.DataFrame(alternatives)
                        st.subheader("Healthier Alternatives")
                        st.dataframe(alternatives_df)
                else:
                    if not alternatives.empty:
                        st.subheader("Healthier Alternatives")
                        st.dataframe(alternatives)
                    else:
                        st.error("Could not find healthier alternatives for this food.")
            else:
                st.error("Could not find healthier alternatives for this food.")
