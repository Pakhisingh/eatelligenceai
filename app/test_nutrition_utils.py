import pandas as pd
import numpy as np
from app.nutrition_utils import load_nutrition_data
import os

def test_load_nutrition_data():
    # Create a sample CSV file for testing
    test_data = {
        'Food': ['Apple', 'Banana', 'Chicken', 'Rice', 'Broccoli'],
        'Calories': ['100', '105', '165', '130', '55'],
        'Protein': ['0.5', '1.3', '31', '2.7', '2.8'],
        'Fat': ['0.3', '0.4', '3.6', '0.3', '0.6'],
        'Carbs': ['25', '27', '0', '28', '11'],
        'Notes': ['Fresh', 'Ripe', 'Grilled', 'White', 'Steamed']
    }
    
    # Create a test DataFrame
    test_df = pd.DataFrame(test_data)
    
    # Save to CSV
    test_df.to_csv('test_nutrition_data.csv', index=False)
    
    try:
        # Test the function
        result_df = load_nutrition_data('test_nutrition_data.csv')
        
        # Verify the results
        assert isinstance(result_df, pd.DataFrame), "Result should be a DataFrame"
        assert len(result_df) == 5, "Should have 5 rows"
        assert all(col in result_df.columns for col in ['Calories', 'Protein', 'Fat', 'Carbs']), "Required columns should be present"
        assert not result_df.isnull().any().any(), "No null values should be present"
        
        # Verify numeric conversion
        assert pd.api.types.is_numeric_dtype(result_df['Calories']), "Calories should be numeric"
        assert pd.api.types.is_numeric_dtype(result_df['Protein']), "Protein should be numeric"
        assert pd.api.types.is_numeric_dtype(result_df['Fat']), "Fat should be numeric"
        assert pd.api.types.is_numeric_dtype(result_df['Carbs']), "Carbs should be numeric"
        
        print("All tests passed successfully!")
        
    finally:
        # Clean up the test file
        if os.path.exists('test_nutrition_data.csv'):
            os.remove('test_nutrition_data.csv')

if __name__ == "__main__":
    test_load_nutrition_data() 