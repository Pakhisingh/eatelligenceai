import streamlit as st
from nutrition_utils import load_nutrition_data
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Nutrition Information",
    page_icon="🥗",
    layout="centered"
)

# Title and description
st.title("🥗 Nutrition Information Lookup")
st.markdown("Enter a food name to see its nutritional information.")

# Load the nutrition data
@st.cache_data
def load_data():
    return load_nutrition_data()

# Load the data
try:
    df = load_data()
    
    # Create a search input
    food_name = st.text_input(
        "Enter a food name:",
        placeholder="e.g., Apple, Chicken, Rice..."
    )
    
    if food_name:
        # Search for the food (case-insensitive)
        results = df[df['Food'].str.contains(food_name, case=False, na=False)]
        
        if len(results) > 0:
            # Display the results
            st.subheader("Nutrition Information")
            
            # Format the display
            for _, row in results.iterrows():
                st.markdown(f"### {row['Food']}")
                
                # Create columns for better layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Calories", f"{row['Calories']} kcal")
                    st.metric("Protein", f"{row['Protein']}g")
                
                with col2:
                    st.metric("Fat", f"{row['Fat']}g")
                    st.metric("Carbohydrates", f"{row['Carbs']}g")
                
                # Add a separator between items
                st.divider()
        else:
            st.warning("No matching food items found. Try a different search term.")
    
    # Show a sample of available foods
    with st.expander("View Available Foods"):
        st.dataframe(df[['Food']].sort_values('Food'), use_container_width=True)
        
except Exception as e:
    st.error(f"Error loading nutrition data: {str(e)}")
    st.info("Please make sure the nutrition_data.csv file exists in the correct location.") 