from typing import Dict, List, Tuple

class HealthyAlternatives:
    def __init__(self):
        # Define common fast food items and their healthier alternatives
        self.alternatives = {
            'samosa': [
                {
                    'name': 'Baked Vegetable Pockets',
                    'ingredients': ['Whole wheat flour', 'Mixed vegetables', 'Low-fat paneer', 'Herbs'],
                    'benefits': [
                        'Lower in calories and fat due to baking instead of deep frying',
                        'Higher in fiber and protein',
                        'Contains essential vitamins from vegetables'
                    ]
                },
                {
                    'name': 'Sprouted Moong Chaat',
                    'ingredients': ['Sprouted moong beans', 'Cucumber', 'Tomato', 'Lemon juice', 'Mint chutney'],
                    'benefits': [
                        'Rich in plant-based protein and fiber',
                        'Low in calories and fat',
                        'Contains digestive enzymes and probiotics'
                    ]
                }
            ],
            'pav bhaji': [
                {
                    'name': 'Multigrain Pav with Vegetable Mash',
                    'ingredients': ['Multigrain bread', 'Mixed vegetables', 'Low-fat butter', 'Herbs'],
                    'benefits': [
                        'Higher in fiber and complex carbohydrates',
                        'Lower in refined flour and fat',
                        'More balanced macronutrient profile'
                    ]
                },
                {
                    'name': 'Quinoa Vegetable Bowl',
                    'ingredients': ['Quinoa', 'Mixed vegetables', 'Low-fat yogurt', 'Herbs'],
                    'benefits': [
                        'Complete protein source',
                        'Rich in fiber and essential nutrients',
                        'Lower glycemic index'
                    ]
                }
            ],
            'vada pav': [
                {
                    'name': 'Grilled Paneer Sandwich',
                    'ingredients': ['Multigrain bread', 'Grilled paneer', 'Mint chutney', 'Vegetables'],
                    'benefits': [
                        'Higher in protein and lower in carbs',
                        'Contains healthy fats from paneer',
                        'Rich in calcium and other minerals'
                    ]
                },
                {
                    'name': 'Sprouted Moong Tikki Burger',
                    'ingredients': ['Sprouted moong patty', 'Whole wheat bun', 'Vegetables', 'Mint chutney'],
                    'benefits': [
                        'High in plant-based protein',
                        'Rich in fiber and essential amino acids',
                        'Lower in calories and fat'
                    ]
                }
            ],
            'dosa': [
                {
                    'name': 'Millet Dosa',
                    'ingredients': ['Foxtail millet', 'Urad dal', 'Vegetables', 'Coconut chutney'],
                    'benefits': [
                        'Higher in protein and fiber',
                        'Rich in essential minerals',
                        'Lower glycemic index'
                    ]
                },
                {
                    'name': 'Quinoa Dosa',
                    'ingredients': ['Quinoa', 'Urad dal', 'Vegetables', 'Mint chutney'],
                    'benefits': [
                        'Complete protein source',
                        'Rich in fiber and antioxidants',
                        'Gluten-free alternative'
                    ]
                }
            ],
            'puri bhaji': [
                {
                    'name': 'Multigrain Roti with Vegetable Curry',
                    'ingredients': ['Multigrain flour', 'Mixed vegetables', 'Low-fat yogurt', 'Herbs'],
                    'benefits': [
                        'Lower in refined flour and oil',
                        'Higher in fiber and protein',
                        'More balanced meal'
                    ]
                },
                {
                    'name': 'Quinoa Upma with Vegetables',
                    'ingredients': ['Quinoa', 'Mixed vegetables', 'Herbs', 'Lemon juice'],
                    'benefits': [
                        'Complete protein source',
                        'Rich in fiber and essential nutrients',
                        'Lower glycemic index'
                    ]
                }
            ],
            'bhel puri': [
                {
                    'name': 'Sprouted Chana Chaat',
                    'ingredients': ['Sprouted chana', 'Cucumber', 'Tomato', 'Lemon juice', 'Herbs'],
                    'benefits': [
                        'Higher in protein and fiber',
                        'Lower in refined flour and oil',
                        'Rich in essential nutrients'
                    ]
                },
                {
                    'name': 'Quinoa Bhel',
                    'ingredients': ['Quinoa', 'Vegetables', 'Lemon juice', 'Herbs', 'Roasted peanuts'],
                    'benefits': [
                        'Complete protein source',
                        'Rich in fiber and healthy fats',
                        'Lower glycemic index'
                    ]
                }
            ],
            'pakora': [
                {
                    'name': 'Baked Vegetable Fritters',
                    'ingredients': ['Mixed vegetables', 'Besan', 'Herbs', 'Olive oil'],
                    'benefits': [
                        'Lower in calories and fat',
                        'Higher in fiber and protein',
                        'Contains essential vitamins'
                    ]
                },
                {
                    'name': 'Roasted Chana',
                    'ingredients': ['Roasted chana', 'Herbs', 'Lemon juice'],
                    'benefits': [
                        'High in plant-based protein',
                        'Rich in fiber and minerals',
                        'Low in fat and calories'
                    ]
                }
            ],
            'paneer tikka': [
                {
                    'name': 'Grilled Paneer with Vegetables',
                    'ingredients': ['Low-fat paneer', 'Bell peppers', 'Onion', 'Herbs', 'Olive oil'],
                    'benefits': [
                        'Lower in calories and fat',
                        'Higher in protein and fiber',
                        'Rich in antioxidants'
                    ]
                },
                {
                    'name': 'Tofu Tikka',
                    'ingredients': ['Tofu', 'Vegetables', 'Herbs', 'Olive oil'],
                    'benefits': [
                        'Lower in saturated fat',
                        'Rich in plant-based protein',
                        'Contains isoflavones'
                    ]
                }
            ],
            'aloo tikki': [
                {
                    'name': 'Sweet Potato Tikki',
                    'ingredients': ['Sweet potato', 'Herbs', 'Olive oil'],
                    'benefits': [
                        'Lower glycemic index',
                        'Higher in fiber and vitamins',
                        'Rich in antioxidants'
                    ]
                },
                {
                    'name': 'Moong Dal Tikki',
                    'ingredients': ['Moong dal', 'Vegetables', 'Herbs', 'Olive oil'],
                    'benefits': [
                        'High in plant-based protein',
                        'Rich in fiber and minerals',
                        'Lower in carbohydrates'
                    ]
                }
            ],
            'pizza': [
                {
                    'name': 'Multigrain Vegetable Pizza',
                    'ingredients': ['Multigrain base', 'Low-fat cheese', 'Vegetables', 'Herbs'],
                    'benefits': [
                        'Higher in fiber and protein',
                        'Lower in refined flour and fat',
                        'More balanced meal'
                    ]
                },
                {
                    'name': 'Quinoa Pizza Bowl',
                    'ingredients': ['Quinoa', 'Vegetables', 'Low-fat cheese', 'Herbs'],
                    'benefits': [
                        'Complete protein source',
                        'Rich in fiber and nutrients',
                        'Lower glycemic index'
                    ]
                }
            ]
        }
    
    def get_alternatives(self, food_item: str) -> List[Dict]:
        """
        Get healthier alternatives for a given fast food item
        
        Args:
            food_item (str): Name of the fast food item
            
        Returns:
            List[Dict]: List of healthier alternatives with their benefits
        """
        return self.alternatives.get(food_item.lower(), [])
    
    def get_all_food_items(self) -> List[str]:
        """
        Get list of all available fast food items
        
        Returns:
            List[str]: List of fast food items
        """
        return list(self.alternatives.keys()) 