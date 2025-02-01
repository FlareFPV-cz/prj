import pandas as pd
import json
import numpy as np

def generate_training_examples(data_path):
    # Read the augmented soil data
    df = pd.read_csv(data_path)
    
    # Define soil condition descriptions
    soil_descriptions = {
        'Acidic_Organic': {
            'properties': 'High organic content with acidic pH levels',
            'improvements': 'Consider adding lime to balance pH and maintain organic matter',
            'crops': ['Blueberries', 'Potatoes', 'Rhododendrons'],
            'impact': 'Supports acid-loving plants but may limit nutrient availability',
            'practices': ['pH monitoring', 'Organic matter management', 'Careful fertilization'],
            'water': 'Good water retention but may need drainage monitoring'
        },
        'Neutral_HighFertility': {
            'properties': 'Balanced pH with high nutrient availability',
            'improvements': 'Maintain organic matter levels and nutrient balance',
            'crops': ['Wheat', 'Corn', 'Soybeans'],
            'impact': 'Optimal for most crops with minimal environmental impact',
            'practices': ['Crop rotation', 'Cover cropping', 'Minimal tillage'],
            'water': 'Good water-holding capacity with efficient drainage'
        },
        'Sandy_LowFertility': {
            'properties': 'High sand content with low nutrient retention',
            'improvements': 'Add organic matter and implement nutrient management',
            'crops': ['Carrots', 'Radishes', 'Lavender'],
            'impact': 'Prone to nutrient leaching and erosion',
            'practices': ['Frequent fertilization', 'Mulching', 'Wind protection'],
            'water': 'Requires frequent irrigation with good drainage'
        },
        'Clayey_PoorDrainage': {
            'properties': 'High clay content with slow drainage',
            'improvements': 'Improve soil structure and drainage',
            'crops': ['Rice', 'Cattails', 'Willows'],
            'impact': 'May contribute to waterlogging and compaction',
            'practices': ['Deep tillage', 'Raised beds', 'Careful irrigation'],
            'water': 'Needs drainage management to prevent waterlogging'
        },
        'Calcareous': {
            'properties': 'High pH with calcium carbonate presence',
            'improvements': 'Monitor micronutrient availability',
            'crops': ['Grapes', 'Olives', 'Alfalfa'],
            'impact': 'May limit certain nutrient availability',
            'practices': ['Micronutrient supplementation', 'Acid-forming fertilizers'],
            'water': 'Moderate water retention with good structure'
        }
    }
    
    training_examples = []
    
    for _, row in df.iterrows():
        soil_type = row['soil_type']
        if soil_type in soil_descriptions:
            desc = soil_descriptions[soil_type]
            
            # Create example with soil data summary
            soil_summary = f"wv0010 (0-5cm): Median {row['wv0010_0_5_Q0.5']:.2f}, Mean {row['wv0010_0_5_mean']:.2f}"
            
            # Generate prompt and completion pair
            prompt = f"Provide actionable insights on soil conditions and crop recommendations:\n\n"
            prompt += f"**Condition**: {soil_type}\n"
            prompt += f"**Confidence**: {np.random.uniform(0.7, 0.95):.2f}\n"
            prompt += f"**Recommendation**: {', '.join(desc['crops'])}\n\n"
            prompt += f"**Soil Data**:\n{soil_summary}\n\n"
            prompt += "### Insights Required:\n"
            prompt += "1. **Soil Properties**: Identify key properties affecting soil health and suggest improvements.\n"
            prompt += "2. **Crop Suitability**: Recommend specific crops that thrive in the current soil condition.\n"
            prompt += "3. **Environmental Impact**: Assess how soil conditions affect the local ecosystem and suggest mitigation strategies.\n"
            prompt += "4. **Management Practices**: Provide detailed practices to enhance soil quality and crop yield.\n"
            prompt += "5. **Water Management**: Offer strategies to optimize water usage and improve irrigation efficiency.\n"
            prompt += "### Begin your detailed response below:\n\n"
            
            completion = f"Based on the soil analysis:\n\n"
            completion += f"1. **Soil Properties**: {desc['properties']}. {desc['improvements']}.\n\n"
            completion += f"2. **Crop Suitability**: Ideal crops include {', '.join(desc['crops'])} which are well-adapted to these conditions.\n\n"
            completion += f"3. **Environmental Impact**: {desc['impact']}.\n\n"
            completion += f"4. **Management Practices**: Recommended practices include {', '.join(desc['practices'])}.\n\n"
            completion += f"5. **Water Management**: {desc['water']}.\n"
            
            training_examples.append({
                'prompt': prompt,
                'completion': completion
            })
    
    # Save training examples to JSON file
    with open('backend/ml/training_data.json', 'w') as f:
        json.dump(training_examples, f, indent=2)
    
    print(f"Generated {len(training_examples)} training examples")

if __name__ == "__main__":
    generate_training_examples('backend/ml/augmented_soil_data.csv')