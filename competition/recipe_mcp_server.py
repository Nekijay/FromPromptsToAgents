"""
Recipe MCP Server - Extended with Budget & Nutrition
=====================================================
Competition: Smart Budget RobotChef
University of Hertfordshire - 18 April 2026

Extends Session 4/5 recipe server with:
  - price_per_serving_gbp, protein_g, calories_kcal, key_vitamins per dish
  - Dietary flags: is_vegetarian, is_vegan, is_gluten_free
  - Shopping lists with per-item costs
  - New tools: get_nutrition, get_price, fit_budget
"""

import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Smart Budget Recipe Agent")

# ---------------------------------------------------------------------------
# Unified Dish Database  (robotic cooking data + budget/nutrition data)
# ---------------------------------------------------------------------------

DISH_DATABASE = {
    "pasta_carbonara": {
        "key": "pasta_carbonara",
        "name": "Pasta Carbonara",
        "cuisine": "Italian",
        "difficulty": "intermediate",
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "servings": 4,
        # --- Budget & Nutrition ---
        "price_per_serving_gbp": 3.50,
        "protein_g_per_serving": 28,
        "calories_kcal_per_serving": 650,
        "key_vitamins": ["B12", "B6", "niacin", "riboflavin"],
        "is_vegetarian": False,
        "is_vegan": False,
        "is_gluten_free": False,
        "shopping_list": [
            {"item": "spaghetti", "qty": "400g", "cost_gbp": 1.20},
            {"item": "guanciale (or pancetta)", "qty": "200g", "cost_gbp": 2.80},
            {"item": "egg yolks", "qty": "6", "cost_gbp": 0.90},
            {"item": "whole eggs", "qty": "2", "cost_gbp": 0.40},
            {"item": "pecorino romano", "qty": "100g", "cost_gbp": 2.50},
            {"item": "parmesan", "qty": "50g", "cost_gbp": 1.20},
            {"item": "black pepper", "qty": "to taste", "cost_gbp": 0.20},
        ],
        # --- Robotic cooking data ---
        "ingredients": [
            {"item": "spaghetti", "quantity": "400g", "prep": "none"},
            {"item": "guanciale", "quantity": "200g", "prep": "cut into strips"},
            {"item": "egg yolks", "quantity": "6", "prep": "separated"},
            {"item": "whole eggs", "quantity": "2", "prep": "beaten"},
            {"item": "pecorino romano", "quantity": "100g", "prep": "finely grated"},
            {"item": "parmesan", "quantity": "50g", "prep": "finely grated"},
            {"item": "black pepper", "quantity": "to taste", "prep": "freshly ground"},
        ],
        "techniques": [
            {"name": "boiling", "description": "Cook pasta in salted boiling water until al dente",
             "precision": "medium", "temperature_c": 100, "duration_minutes": 10},
            {"name": "rendering fat", "description": "Slowly render fat from guanciale over medium-low heat",
             "precision": "high", "temperature_c": 130, "duration_minutes": 8},
            {"name": "emulsification", "description": "Combine egg mixture with hot pasta off heat",
             "precision": "critical", "temperature_c": 65, "duration_minutes": 2},
        ],
        "equipment": ["large pot", "sauté pan", "mixing bowl", "tongs", "colander"],
        "temperatures": {"water_boil": 100, "guanciale_render": 130, "sauce_emulsify": 65, "serving": 70},
        "steps": [
            "Bring a large pot of salted water to a rolling boil.",
            "Cut guanciale into 5mm strips.",
            "Whisk egg yolks, whole eggs, and grated cheeses together.",
            "Cook guanciale in a dry pan over medium-low heat until fat renders (8 min).",
            "Cook spaghetti until al dente (about 10 min). Reserve 200ml pasta water.",
            "Remove pan from heat. Add drained pasta to the guanciale pan.",
            "Pour egg and cheese mixture over pasta, tossing vigorously off heat.",
            "Add pasta water a splash at a time for silky consistency.",
            "Season with freshly ground black pepper and serve immediately.",
        ],
        "safety": [
            "Render guanciale slowly to avoid grease splatter.",
            "Remove pan from heat before adding eggs to prevent scrambling.",
            "Serve immediately — carbonara does not reheat well.",
        ],
    },

    "cheese_souffle": {
        "key": "cheese_souffle",
        "name": "Cheese Soufflé",
        "cuisine": "French",
        "difficulty": "advanced",
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "servings": 4,
        "price_per_serving_gbp": 2.80,
        "protein_g_per_serving": 18,
        "calories_kcal_per_serving": 420,
        "key_vitamins": ["A", "D", "B12", "calcium"],
        "is_vegetarian": True,
        "is_vegan": False,
        "is_gluten_free": False,
        "shopping_list": [
            {"item": "butter", "qty": "50g", "cost_gbp": 0.40},
            {"item": "plain flour", "qty": "40g", "cost_gbp": 0.15},
            {"item": "whole milk", "qty": "300ml", "cost_gbp": 0.45},
            {"item": "gruyère cheese", "qty": "150g", "cost_gbp": 3.00},
            {"item": "eggs", "qty": "9 (4 yolks + 5 whites)", "cost_gbp": 1.80},
            {"item": "dijon mustard", "qty": "1 tsp", "cost_gbp": 0.20},
        ],
        "ingredients": [
            {"item": "butter", "quantity": "50g", "prep": "melted"},
            {"item": "plain flour", "quantity": "40g", "prep": "sifted"},
            {"item": "whole milk", "quantity": "300ml", "prep": "warmed"},
            {"item": "gruyère cheese", "quantity": "150g", "prep": "finely grated"},
            {"item": "egg yolks", "quantity": "4", "prep": "separated"},
            {"item": "egg whites", "quantity": "5", "prep": "room temperature"},
            {"item": "dijon mustard", "quantity": "1 tsp", "prep": "none"},
        ],
        "techniques": [
            {"name": "roux making", "description": "Cook butter and flour together",
             "precision": "high", "temperature_c": 120, "duration_minutes": 3},
            {"name": "béchamel sauce", "description": "Whisk warm milk into roux",
             "precision": "high", "temperature_c": 85, "duration_minutes": 5},
            {"name": "whipping egg whites", "description": "Whip egg whites to stiff peaks",
             "precision": "critical", "temperature_c": 20, "duration_minutes": 5},
            {"name": "folding", "description": "Gently fold egg whites into cheese base",
             "precision": "critical", "temperature_c": 40, "duration_minutes": 2},
            {"name": "baking", "description": "Bake in preheated oven without opening door",
             "precision": "critical", "temperature_c": 190, "duration_minutes": 25},
        ],
        "equipment": ["soufflé ramekins", "saucepan", "whisk", "electric mixer", "spatula", "oven"],
        "temperatures": {"roux": 120, "bechamel": 85, "oven": 190, "egg_whites": 20},
        "steps": [
            "Preheat oven to 190°C. Butter ramekins and dust with parmesan.",
            "Melt butter, stir in flour, cook roux for 2-3 minutes.",
            "Gradually whisk in warm milk to create smooth béchamel.",
            "Remove from heat. Stir in gruyère, mustard, salt, pepper.",
            "Beat in egg yolks one at a time.",
            "Whip egg whites to stiff peaks.",
            "Fold whites into cheese base in three additions.",
            "Fill ramekins to three-quarters. Run thumb around rim.",
            "Bake for 25 minutes. Do not open oven door. Serve immediately.",
        ],
        "safety": [
            "Do not open oven door during baking or soufflé will collapse.",
            "Handle hot ramekins with oven gloves.",
            "Ensure no yolk contaminates egg whites.",
        ],
    },

    "sushi_rolls": {
        "key": "sushi_rolls",
        "name": "Sushi Rolls (Maki)",
        "cuisine": "Japanese",
        "difficulty": "intermediate",
        "prep_time_minutes": 45,
        "cook_time_minutes": 20,
        "servings": 4,
        "price_per_serving_gbp": 5.50,
        "protein_g_per_serving": 22,
        "calories_kcal_per_serving": 380,
        "key_vitamins": ["B12", "D", "omega-3", "iodine"],
        "is_vegetarian": False,
        "is_vegan": False,
        "is_gluten_free": True,
        "shopping_list": [
            {"item": "sushi rice", "qty": "400g", "cost_gbp": 1.60},
            {"item": "rice vinegar", "qty": "60ml", "cost_gbp": 0.40},
            {"item": "nori sheets", "qty": "8", "cost_gbp": 1.50},
            {"item": "fresh salmon (sushi-grade)", "qty": "200g", "cost_gbp": 6.00},
            {"item": "cucumber", "qty": "1", "cost_gbp": 0.60},
            {"item": "avocado", "qty": "2", "cost_gbp": 1.60},
            {"item": "soy sauce, wasabi, pickled ginger", "qty": "to serve", "cost_gbp": 0.50},
        ],
        "ingredients": [
            {"item": "sushi rice", "quantity": "400g", "prep": "washed and drained"},
            {"item": "rice vinegar", "quantity": "60ml", "prep": "seasoned with sugar and salt"},
            {"item": "nori sheets", "quantity": "8", "prep": "halved if needed"},
            {"item": "fresh salmon", "quantity": "200g", "prep": "cut into thin strips"},
            {"item": "cucumber", "quantity": "1", "prep": "julienned"},
            {"item": "avocado", "quantity": "2", "prep": "thinly sliced"},
        ],
        "techniques": [
            {"name": "rice cooking", "description": "Cook sushi rice with precise water ratio",
             "precision": "high", "temperature_c": 100, "duration_minutes": 15},
            {"name": "rice seasoning", "description": "Season hot rice with vinegar while fanning",
             "precision": "high", "temperature_c": 60, "duration_minutes": 5},
            {"name": "precision cutting", "description": "Cut fish into uniform strips",
             "precision": "critical", "temperature_c": 4, "duration_minutes": 10},
            {"name": "rolling", "description": "Tightly roll sushi with even pressure",
             "precision": "high", "temperature_c": 20, "duration_minutes": 3},
        ],
        "equipment": ["rice cooker", "hangiri", "bamboo rolling mat", "sharp sushi knife", "cutting board"],
        "temperatures": {"rice_cooking": 100, "rice_serving": 37, "fish_storage": 4, "assembly": 20},
        "steps": [
            "Wash sushi rice until water runs clear. Cook with 1:1.1 rice-to-water ratio.",
            "Mix rice vinegar, sugar, salt. Season hot rice while fanning to cool.",
            "Slice salmon into 1cm strips. Keep refrigerated at 4°C until needed.",
            "Place nori on bamboo mat. Spread thin even layer of rice, leaving 1cm border.",
            "Lay fish, cucumber, avocado across centre. Roll tightly.",
            "Wet a sharp knife. Slice each roll into 6-8 pieces with single clean cuts.",
        ],
        "safety": [
            "Keep raw fish at 4°C or below until ready to use.",
            "Use sushi-grade fish from a reputable supplier.",
            "Clean all surfaces after handling raw fish.",
        ],
    },

    "pizza_margherita": {
        "key": "pizza_margherita",
        "name": "Pizza Margherita",
        "cuisine": "Italian",
        "difficulty": "intermediate",
        "prep_time_minutes": 120,
        "cook_time_minutes": 10,
        "servings": 4,
        "price_per_serving_gbp": 2.50,
        "protein_g_per_serving": 15,
        "calories_kcal_per_serving": 500,
        "key_vitamins": ["A", "C", "B3", "lycopene"],
        "is_vegetarian": True,
        "is_vegan": False,
        "is_gluten_free": False,
        "shopping_list": [
            {"item": "tipo 00 flour", "qty": "500g", "cost_gbp": 1.20},
            {"item": "fresh yeast", "qty": "3g", "cost_gbp": 0.20},
            {"item": "San Marzano tomatoes", "qty": "400g tin", "cost_gbp": 1.00},
            {"item": "fresh mozzarella", "qty": "250g", "cost_gbp": 2.50},
            {"item": "fresh basil", "qty": "handful", "cost_gbp": 0.60},
            {"item": "extra virgin olive oil", "qty": "2 tbsp", "cost_gbp": 0.30},
        ],
        "ingredients": [
            {"item": "tipo 00 flour", "quantity": "500g", "prep": "sifted"},
            {"item": "water", "quantity": "325ml", "prep": "lukewarm (35°C)"},
            {"item": "fresh yeast", "quantity": "3g", "prep": "crumbled"},
            {"item": "san marzano tomatoes", "quantity": "400g", "prep": "crushed by hand"},
            {"item": "fresh mozzarella", "quantity": "250g", "prep": "torn into pieces"},
            {"item": "fresh basil", "quantity": "handful", "prep": "leaves picked"},
        ],
        "techniques": [
            {"name": "dough kneading", "description": "Knead dough until smooth and elastic",
             "precision": "high", "temperature_c": 25, "duration_minutes": 15},
            {"name": "fermentation", "description": "Allow dough to ferment and rise",
             "precision": "medium", "temperature_c": 25, "duration_minutes": 120},
            {"name": "stretching", "description": "Stretch dough into thin disc by hand",
             "precision": "high", "temperature_c": 25, "duration_minutes": 3},
            {"name": "high-heat baking", "description": "Bake at maximum temperature on hot stone",
             "precision": "high", "temperature_c": 300, "duration_minutes": 7},
        ],
        "equipment": ["mixing bowl", "pizza stone or steel", "oven", "pizza peel", "bench scraper"],
        "temperatures": {"water": 35, "fermentation": 25, "oven": 300, "serving": 75},
        "steps": [
            "Dissolve yeast in 35°C water. Combine with flour and salt.",
            "Knead for 15 minutes. Ferment for 2 hours in oiled bowl.",
            "Preheat oven with pizza stone to 300°C (max).",
            "Stretch each dough ball into a 30cm disc by hand.",
            "Spread crushed tomatoes, add torn mozzarella.",
            "Bake 6-7 minutes. Add fresh basil and olive oil. Serve immediately.",
        ],
        "safety": [
            "Pizza stone reaches extremely high temperatures — use pizza peel.",
            "Do not touch oven interior without protection.",
        ],
    },

    "beef_stir_fry": {
        "key": "beef_stir_fry",
        "name": "Beef Stir-Fry",
        "cuisine": "Chinese",
        "difficulty": "beginner",
        "prep_time_minutes": 20,
        "cook_time_minutes": 10,
        "servings": 4,
        "price_per_serving_gbp": 4.50,
        "protein_g_per_serving": 35,
        "calories_kcal_per_serving": 480,
        "key_vitamins": ["B12", "B6", "iron", "zinc"],
        "is_vegetarian": False,
        "is_vegan": False,
        "is_gluten_free": False,
        "shopping_list": [
            {"item": "beef sirloin", "qty": "500g", "cost_gbp": 8.00},
            {"item": "soy sauce", "qty": "3 tbsp", "cost_gbp": 0.40},
            {"item": "oyster sauce", "qty": "2 tbsp", "cost_gbp": 0.40},
            {"item": "bell peppers", "qty": "2", "cost_gbp": 1.00},
            {"item": "broccoli", "qty": "200g", "cost_gbp": 0.80},
            {"item": "garlic & ginger", "qty": "4 cloves + 2cm", "cost_gbp": 0.50},
            {"item": "spring onions", "qty": "4", "cost_gbp": 0.50},
            {"item": "vegetable oil", "qty": "3 tbsp", "cost_gbp": 0.20},
            {"item": "cornstarch", "qty": "1 tbsp", "cost_gbp": 0.10},
        ],
        "ingredients": [
            {"item": "beef sirloin", "quantity": "500g", "prep": "thinly sliced against grain"},
            {"item": "soy sauce", "quantity": "3 tbsp", "prep": "none"},
            {"item": "oyster sauce", "quantity": "2 tbsp", "prep": "none"},
            {"item": "garlic", "quantity": "4 cloves", "prep": "minced"},
            {"item": "fresh ginger", "quantity": "2cm piece", "prep": "julienned"},
            {"item": "bell peppers", "quantity": "2", "prep": "sliced"},
            {"item": "broccoli", "quantity": "200g", "prep": "florets"},
            {"item": "spring onions", "quantity": "4", "prep": "3cm lengths"},
        ],
        "techniques": [
            {"name": "velveting", "description": "Marinate beef with cornstarch to tenderise",
             "precision": "medium", "temperature_c": 4, "duration_minutes": 15},
            {"name": "wok hei", "description": "Stir-fry over extremely high heat",
             "precision": "high", "temperature_c": 300, "duration_minutes": 2},
            {"name": "batch cooking", "description": "Cook in batches to maintain wok temperature",
             "precision": "high", "temperature_c": 300, "duration_minutes": 5},
        ],
        "equipment": ["wok", "wok spatula", "chopping board", "sharp knife", "mixing bowls"],
        "temperatures": {"wok_heat": 300, "oil_shimmer": 200, "serving": 80},
        "steps": [
            "Slice beef thinly against the grain. Marinate with soy sauce and cornstarch 15 min.",
            "Prepare all vegetables before heating the wok (mise en place).",
            "Heat wok over highest heat until it smokes lightly.",
            "Sear beef in single layer for 60 seconds. Remove.",
            "Stir-fry garlic and ginger 15 seconds. Add broccoli and peppers, toss 2 minutes.",
            "Return beef. Add oyster sauce, toss 30 seconds. Add spring onions. Serve over rice.",
        ],
        "safety": [
            "Never add water to a hot oiled wok — violent splatter.",
            "Ensure all ingredients are dry before adding to hot oil.",
            "Use long-handled spatula to avoid burns.",
        ],
    },

    "chocolate_cake": {
        "key": "chocolate_cake",
        "name": "Chocolate Cake",
        "cuisine": "International",
        "difficulty": "intermediate",
        "prep_time_minutes": 25,
        "cook_time_minutes": 35,
        "servings": 12,
        "price_per_serving_gbp": 1.80,
        "protein_g_per_serving": 6,
        "calories_kcal_per_serving": 450,
        "key_vitamins": ["A", "D", "E", "iron"],
        "is_vegetarian": True,
        "is_vegan": False,
        "is_gluten_free": False,
        "shopping_list": [
            {"item": "plain flour", "qty": "300g", "cost_gbp": 0.60},
            {"item": "cocoa powder", "qty": "75g", "cost_gbp": 1.20},
            {"item": "caster sugar", "qty": "350g", "cost_gbp": 0.70},
            {"item": "eggs", "qty": "3", "cost_gbp": 0.60},
            {"item": "buttermilk", "qty": "240ml", "cost_gbp": 0.80},
            {"item": "vegetable oil", "qty": "180ml", "cost_gbp": 0.40},
            {"item": "dark chocolate (ganache)", "qty": "200g", "cost_gbp": 2.00},
            {"item": "double cream (ganache)", "qty": "200ml", "cost_gbp": 1.50},
            {"item": "baking soda, baking powder, vanilla", "qty": "as needed", "cost_gbp": 0.50},
        ],
        "ingredients": [
            {"item": "plain flour", "quantity": "300g", "prep": "sifted"},
            {"item": "cocoa powder", "quantity": "75g", "prep": "sifted"},
            {"item": "caster sugar", "quantity": "350g", "prep": "none"},
            {"item": "eggs", "quantity": "3", "prep": "room temperature"},
            {"item": "buttermilk", "quantity": "240ml", "prep": "room temperature"},
            {"item": "dark chocolate", "quantity": "200g", "prep": "chopped for ganache"},
            {"item": "double cream", "quantity": "200ml", "prep": "heated for ganache"},
        ],
        "techniques": [
            {"name": "mixing", "description": "Combine wet and dry ingredients without overmixing",
             "precision": "medium", "temperature_c": 20, "duration_minutes": 5},
            {"name": "baking", "description": "Bake until skewer comes out clean",
             "precision": "high", "temperature_c": 175, "duration_minutes": 35},
            {"name": "ganache making", "description": "Pour hot cream over chocolate and stir smooth",
             "precision": "high", "temperature_c": 80, "duration_minutes": 5},
            {"name": "frosting", "description": "Apply ganache evenly over cooled cake",
             "precision": "medium", "temperature_c": 30, "duration_minutes": 10},
        ],
        "equipment": ["2x 20cm cake tins", "mixing bowls", "electric mixer", "wire rack", "oven", "saucepan"],
        "temperatures": {"oven": 175, "ganache_cream": 80, "ganache_setting": 20},
        "steps": [
            "Preheat oven to 175°C. Grease and line two 20cm cake tins.",
            "Sift and combine all dry ingredients.",
            "Whisk sugar, eggs, buttermilk, oil, and vanilla together.",
            "Fold dry into wet until just combined. Stir in hot water.",
            "Divide between tins. Bake 30-35 minutes until skewer comes out clean.",
            "Cool completely. Make ganache: pour hot cream over chocolate, stir smooth.",
            "Layer and frost with ganache. Allow to set.",
        ],
        "safety": [
            "Handle hot water carefully when adding to batter.",
            "Allow cake to cool fully before applying ganache.",
        ],
    },

    "fish_and_chips": {
        "key": "fish_and_chips",
        "name": "Fish and Chips",
        "cuisine": "British",
        "difficulty": "intermediate",
        "prep_time_minutes": 20,
        "cook_time_minutes": 30,
        "servings": 4,
        "price_per_serving_gbp": 4.00,
        "protein_g_per_serving": 30,
        "calories_kcal_per_serving": 720,
        "key_vitamins": ["D", "B12", "B6", "iodine"],
        "is_vegetarian": False,
        "is_vegan": False,
        "is_gluten_free": False,
        "shopping_list": [
            {"item": "cod fillets", "qty": "4 x 200g", "cost_gbp": 7.00},
            {"item": "large potatoes", "qty": "1kg", "cost_gbp": 1.20},
            {"item": "plain flour", "qty": "250g", "cost_gbp": 0.50},
            {"item": "vegetable oil (deep frying)", "qty": "2L", "cost_gbp": 2.00},
            {"item": "cold sparkling water", "qty": "250ml", "cost_gbp": 0.40},
            {"item": "baking powder, cornflour", "qty": "as needed", "cost_gbp": 0.40},
            {"item": "malt vinegar & salt", "qty": "to serve", "cost_gbp": 0.30},
        ],
        "ingredients": [
            {"item": "cod fillets", "quantity": "4 x 200g", "prep": "skinned and boned"},
            {"item": "plain flour", "quantity": "200g", "prep": "sifted"},
            {"item": "cornflour", "quantity": "50g", "prep": "none"},
            {"item": "cold sparkling water", "quantity": "250ml", "prep": "very cold"},
            {"item": "large potatoes", "quantity": "1kg", "prep": "cut into thick chips"},
            {"item": "vegetable oil", "quantity": "2 litres", "prep": "for deep frying"},
        ],
        "techniques": [
            {"name": "double frying chips", "description": "Fry chips twice for crispy finish",
             "precision": "high", "temperature_c": 160, "duration_minutes": 15},
            {"name": "batter making", "description": "Mix cold sparkling water into flour for light batter",
             "precision": "medium", "temperature_c": 4, "duration_minutes": 2},
            {"name": "deep frying fish", "description": "Deep fry battered fish until golden",
             "precision": "high", "temperature_c": 190, "duration_minutes": 6},
        ],
        "equipment": ["deep fryer or large pot", "cooking thermometer", "wire rack", "slotted spoon", "mixing bowl"],
        "temperatures": {"first_fry_chips": 130, "second_fry_chips": 190, "fish_fry": 190, "oil_max_safe": 200},
        "steps": [
            "Peel and cut potatoes into 1.5cm chips. Rinse and dry well.",
            "Blanch chips at 130°C for 6-8 minutes until cooked but not coloured. Drain.",
            "Mix flour, cornflour, baking powder. Whisk in ice-cold sparkling water.",
            "Increase oil to 190°C. Pat fish dry, dust with flour, dip in batter.",
            "Fry fish 5-6 minutes until golden. Drain on wire rack.",
            "Return chips to 190°C oil. Fry 3-4 minutes until crispy. Season and serve.",
        ],
        "safety": [
            "Never fill fryer more than one-third with oil.",
            "Monitor temperature constantly — overheated oil can ignite.",
            "Never use water on an oil fire — use fire blanket or lid.",
        ],
    },

    "pad_thai": {
        "key": "pad_thai",
        "name": "Pad Thai",
        "cuisine": "Thai",
        "difficulty": "intermediate",
        "prep_time_minutes": 25,
        "cook_time_minutes": 10,
        "servings": 4,
        "price_per_serving_gbp": 3.50,
        "protein_g_per_serving": 25,
        "calories_kcal_per_serving": 560,
        "key_vitamins": ["B3", "B6", "E", "potassium"],
        "is_vegetarian": False,
        "is_vegan": False,
        "is_gluten_free": True,
        "shopping_list": [
            {"item": "flat rice noodles", "qty": "250g", "cost_gbp": 1.00},
            {"item": "prawns", "qty": "200g", "cost_gbp": 3.50},
            {"item": "firm tofu", "qty": "150g", "cost_gbp": 1.20},
            {"item": "eggs", "qty": "2", "cost_gbp": 0.40},
            {"item": "bean sprouts", "qty": "150g", "cost_gbp": 0.60},
            {"item": "tamarind paste", "qty": "3 tbsp", "cost_gbp": 0.50},
            {"item": "fish sauce", "qty": "3 tbsp", "cost_gbp": 0.30},
            {"item": "palm sugar", "qty": "2 tbsp", "cost_gbp": 0.30},
            {"item": "roasted peanuts", "qty": "50g", "cost_gbp": 0.40},
            {"item": "limes, garlic chives", "qty": "2 limes + 50g", "cost_gbp": 0.60},
        ],
        "ingredients": [
            {"item": "flat rice noodles", "quantity": "250g", "prep": "soaked in warm water 20 min"},
            {"item": "prawns", "quantity": "200g", "prep": "peeled and deveined"},
            {"item": "firm tofu", "quantity": "150g", "prep": "pressed and cubed"},
            {"item": "eggs", "quantity": "2", "prep": "beaten"},
            {"item": "bean sprouts", "quantity": "150g", "prep": "washed"},
            {"item": "tamarind paste", "quantity": "3 tbsp", "prep": "dissolved in water"},
            {"item": "fish sauce", "quantity": "3 tbsp", "prep": "none"},
        ],
        "techniques": [
            {"name": "noodle soaking", "description": "Soak rice noodles in warm water until pliable",
             "precision": "high", "temperature_c": 40, "duration_minutes": 20},
            {"name": "sauce balancing", "description": "Balance tamarind, fish sauce, palm sugar",
             "precision": "critical", "temperature_c": 20, "duration_minutes": 3},
            {"name": "high-heat wok frying", "description": "Cook at high heat, tossing rapidly",
             "precision": "high", "temperature_c": 250, "duration_minutes": 5},
        ],
        "equipment": ["wok", "wok spatula", "mixing bowls", "chopping board", "sharp knife"],
        "temperatures": {"noodle_soak": 40, "wok_heat": 250, "serving": 80},
        "steps": [
            "Soak rice noodles in warm water for 20 minutes. Drain.",
            "Mix tamarind, fish sauce, and palm sugar into pad thai sauce.",
            "Heat wok on high. Fry tofu until golden. Remove.",
            "Stir-fry garlic, add prawns (1 min), push aside. Scramble eggs.",
            "Add drained noodles and sauce. Toss 1-2 minutes.",
            "Return tofu, add bean sprouts and chives. Top with peanuts and lime.",
        ],
        "safety": [
            "Ensure prawns are fully cooked (pink and opaque).",
            "Wok reaches very high temperatures — use long-handled utensils.",
        ],
    },

    "french_omelette": {
        "key": "french_omelette",
        "name": "French Omelette",
        "cuisine": "French",
        "difficulty": "advanced",
        "prep_time_minutes": 5,
        "cook_time_minutes": 3,
        "servings": 1,
        "price_per_serving_gbp": 1.20,
        "protein_g_per_serving": 20,
        "calories_kcal_per_serving": 280,
        "key_vitamins": ["A", "D", "B12", "choline"],
        "is_vegetarian": True,
        "is_vegan": False,
        "is_gluten_free": True,
        "shopping_list": [
            {"item": "eggs", "qty": "3", "cost_gbp": 0.60},
            {"item": "butter", "qty": "15g", "cost_gbp": 0.20},
            {"item": "fresh herbs (chives, tarragon)", "qty": "1 tbsp", "cost_gbp": 0.20},
            {"item": "salt, white pepper", "qty": "pinch each", "cost_gbp": 0.05},
        ],
        "ingredients": [
            {"item": "eggs", "quantity": "3", "prep": "beaten thoroughly"},
            {"item": "butter", "quantity": "15g", "prep": "none"},
            {"item": "fresh herbs", "quantity": "1 tbsp", "prep": "finely chopped"},
        ],
        "techniques": [
            {"name": "egg beating", "description": "Beat eggs until yolks and whites fully homogeneous",
             "precision": "medium", "temperature_c": 20, "duration_minutes": 1},
            {"name": "pan shaking", "description": "Shake pan while stirring to create creamy curds",
             "precision": "critical", "temperature_c": 150, "duration_minutes": 1},
            {"name": "rolling", "description": "Roll omelette onto plate in smooth motion",
             "precision": "critical", "temperature_c": 65, "duration_minutes": 0.5},
        ],
        "equipment": ["non-stick pan (20cm)", "fork or chopstick", "plate"],
        "temperatures": {"butter_foam": 150, "cooking": 150, "centre_target": 65},
        "steps": [
            "Beat 3 eggs with salt and white pepper until completely homogeneous.",
            "Heat 20cm non-stick pan over medium-high heat.",
            "Add butter. When foam subsides, add eggs.",
            "Stir continuously with fork while shaking pan.",
            "When 80% set with creamy centre, fold one-third over.",
            "Roll onto plate. Rub surface with butter for gloss. Add herbs.",
        ],
        "safety": [
            "Pan is very hot — avoid touching cooking surface.",
            "Work quickly — entire cook takes 60-90 seconds.",
        ],
    },

    "artisan_bread": {
        "key": "artisan_bread",
        "name": "Artisan Bread",
        "cuisine": "International",
        "difficulty": "intermediate",
        "prep_time_minutes": 30,
        "cook_time_minutes": 45,
        "servings": 12,
        "price_per_serving_gbp": 0.30,
        "protein_g_per_serving": 4,
        "calories_kcal_per_serving": 150,
        "key_vitamins": ["B1", "B3", "iron", "folate"],
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": False,
        "shopping_list": [
            {"item": "strong bread flour", "qty": "500g", "cost_gbp": 0.80},
            {"item": "instant yeast", "qty": "7g", "cost_gbp": 0.30},
            {"item": "salt", "qty": "10g", "cost_gbp": 0.05},
            {"item": "olive oil", "qty": "1 tbsp", "cost_gbp": 0.10},
        ],
        "ingredients": [
            {"item": "strong bread flour", "quantity": "500g", "prep": "none"},
            {"item": "water", "quantity": "350ml", "prep": "lukewarm (37°C)"},
            {"item": "salt", "quantity": "10g", "prep": "fine"},
            {"item": "instant yeast", "quantity": "7g", "prep": "none"},
        ],
        "techniques": [
            {"name": "kneading", "description": "Knead dough to develop gluten until smooth",
             "precision": "high", "temperature_c": 25, "duration_minutes": 12},
            {"name": "bulk fermentation", "description": "First rise at room temperature",
             "precision": "medium", "temperature_c": 25, "duration_minutes": 90},
            {"name": "shaping", "description": "Shape into boule with good surface tension",
             "precision": "high", "temperature_c": 25, "duration_minutes": 5},
            {"name": "steam baking", "description": "Bake with steam for oven spring and crust",
             "precision": "critical", "temperature_c": 230, "duration_minutes": 40},
        ],
        "equipment": ["mixing bowl", "bench scraper", "banneton", "dutch oven", "oven", "lame"],
        "temperatures": {"water": 37, "fermentation": 25, "oven_initial": 230, "oven_reduced": 210},
        "steps": [
            "Combine flour, salt, yeast. Add 37°C water. Mix to shaggy dough.",
            "Knead 10-12 minutes until smooth. Ferment 90 minutes until doubled.",
            "Shape into boule. Place seam-up in floured banneton. Proof 45 minutes.",
            "Preheat oven to 230°C with Dutch oven inside.",
            "Turn dough into hot Dutch oven. Score the top.",
            "Bake covered 25 minutes (steam). Remove lid, reduce to 210°C, bake 15-20 more.",
        ],
        "safety": [
            "Dutch oven is extremely hot (230°C) — always use oven gloves.",
            "Scoring requires a very sharp blade — cut away from body.",
        ],
    },
}


# ---------------------------------------------------------------------------
# Python-callable helpers (also used by MCP tools and importable by agents.py)
# ---------------------------------------------------------------------------

def _find_dish(name: str):
    """Fuzzy-match a dish name and return (key, dish_dict) or (None, None)."""
    key = name.lower().strip().replace(" ", "_").replace("-", "_")
    if key in DISH_DATABASE:
        return key, DISH_DATABASE[key]
    for k, d in DISH_DATABASE.items():
        if key in k or k in key or name.lower() in d["name"].lower():
            return k, d
    return None, None


def find_best_dish(budget_gbp: float, people: int, dietary_filter: str = "none") -> dict | None:
    """
    Return the best dish (highest protein) that fits within budget.
    Applies dietary filter if specified.
    """
    affordable = []
    for key, dish in DISH_DATABASE.items():
        total_cost = dish["price_per_serving_gbp"] * people
        if total_cost > budget_gbp:
            continue
        if dietary_filter == "vegetarian" and not dish["is_vegetarian"]:
            continue
        if dietary_filter == "vegan" and not dish["is_vegan"]:
            continue
        if dietary_filter == "gluten-free" and not dish["is_gluten_free"]:
            continue
        affordable.append({
            "key": key,
            "name": dish["name"],
            "total_cost_gbp": round(total_cost, 2),
            "protein_g_per_serving": dish["protein_g_per_serving"],
            "calories_kcal_per_serving": dish["calories_kcal_per_serving"],
            "key_vitamins": dish["key_vitamins"],
            "is_vegetarian": dish["is_vegetarian"],
            "is_vegan": dish["is_vegan"],
            "is_gluten_free": dish["is_gluten_free"],
            "shopping_list": dish.get("shopping_list", []),
        })
    affordable.sort(key=lambda x: x["protein_g_per_serving"], reverse=True)
    return affordable[0] if affordable else None


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def analyse_dish(dish_name: str) -> str:
    """
    Analyse a dish and return structured information: ingredients, techniques,
    equipment, temperatures, and step-by-step instructions.

    Args:
        dish_name: Name of the dish (e.g. 'pasta carbonara', 'beef stir-fry')
    """
    _, dish = _find_dish(dish_name)
    if dish is None:
        return json.dumps({
            "error": f"Dish '{dish_name}' not found.",
            "available_dishes": list(DISH_DATABASE.keys()),
        }, indent=2)
    return json.dumps({
        "name": dish["name"],
        "cuisine": dish["cuisine"],
        "difficulty": dish["difficulty"],
        "servings": dish["servings"],
        "total_time_minutes": dish["prep_time_minutes"] + dish["cook_time_minutes"],
        "ingredients": dish["ingredients"],
        "equipment": dish["equipment"],
        "temperatures": dish["temperatures"],
        "steps": dish["steps"],
        "safety": dish["safety"],
    }, indent=2)


@mcp.tool()
def get_nutrition(dish_name: str) -> str:
    """
    Get nutritional information for a dish: calories, protein, vitamins,
    and dietary flags (vegetarian, vegan, gluten-free).

    Args:
        dish_name: Name of the dish (e.g. 'pasta carbonara')
    """
    _, dish = _find_dish(dish_name)
    if dish is None:
        return json.dumps({
            "error": f"Dish '{dish_name}' not found.",
            "available_dishes": list(DISH_DATABASE.keys()),
        }, indent=2)
    return json.dumps({
        "dish": dish["name"],
        "per_serving": {
            "calories_kcal": dish["calories_kcal_per_serving"],
            "protein_g": dish["protein_g_per_serving"],
            "key_vitamins": dish["key_vitamins"],
        },
        "dietary_flags": {
            "is_vegetarian": dish["is_vegetarian"],
            "is_vegan": dish["is_vegan"],
            "is_gluten_free": dish["is_gluten_free"],
        },
    }, indent=2)


@mcp.tool()
def get_price(dish_name: str, servings: int = 1) -> str:
    """
    Get the price and shopping list for a dish scaled to a number of servings.

    Args:
        dish_name: Name of the dish
        servings: Number of servings to cook (default 1)
    """
    _, dish = _find_dish(dish_name)
    if dish is None:
        return json.dumps({
            "error": f"Dish '{dish_name}' not found.",
            "available_dishes": list(DISH_DATABASE.keys()),
        }, indent=2)
    total_cost = round(dish["price_per_serving_gbp"] * servings, 2)
    return json.dumps({
        "dish": dish["name"],
        "servings": servings,
        "price_per_serving_gbp": dish["price_per_serving_gbp"],
        "total_cost_gbp": total_cost,
        "shopping_list": dish.get("shopping_list", []),
    }, indent=2)


@mcp.tool()
def fit_budget(budget_gbp: float, people: int, dietary_filter: str = "none") -> str:
    """
    Find all dishes that fit within the given budget for the specified number of
    people, filtered by dietary requirements, sorted by protein content.

    Args:
        budget_gbp: Total budget in GBP (e.g. 15.0)
        people: Number of people eating
        dietary_filter: One of 'none', 'vegetarian', 'vegan', 'gluten-free'
    """
    affordable = []
    for key, dish in DISH_DATABASE.items():
        total_cost = dish["price_per_serving_gbp"] * people
        if total_cost > budget_gbp:
            continue
        if dietary_filter == "vegetarian" and not dish["is_vegetarian"]:
            continue
        if dietary_filter == "vegan" and not dish["is_vegan"]:
            continue
        if dietary_filter == "gluten-free" and not dish["is_gluten_free"]:
            continue
        affordable.append({
            "dish": dish["name"],
            "total_cost_gbp": round(total_cost, 2),
            "protein_g_per_serving": dish["protein_g_per_serving"],
            "calories_kcal_per_serving": dish["calories_kcal_per_serving"],
            "is_vegetarian": dish["is_vegetarian"],
            "is_gluten_free": dish["is_gluten_free"],
        })
    affordable.sort(key=lambda x: x["protein_g_per_serving"], reverse=True)

    best = affordable[0] if affordable else None
    return json.dumps({
        "budget_gbp": budget_gbp,
        "people": people,
        "dietary_filter": dietary_filter,
        "affordable_dishes": affordable,
        "best_pick": best,
        "reasoning": (
            f"Best pick '{best['dish']}' chosen for highest protein "
            f"({best['protein_g_per_serving']}g/serving) within £{budget_gbp} budget."
            if best else "No dishes found within budget with these constraints."
        ),
    }, indent=2)


@mcp.tool()
def get_cooking_techniques(dish_name: str) -> str:
    """
    Get a detailed breakdown of cooking techniques required for a dish,
    including precision requirements, temperatures, and durations.

    Args:
        dish_name: Name of the dish
    """
    _, dish = _find_dish(dish_name)
    if dish is None:
        return json.dumps({
            "error": f"Dish '{dish_name}' not found.",
            "available_dishes": list(DISH_DATABASE.keys()),
        }, indent=2)
    return json.dumps({
        "dish": dish["name"],
        "difficulty": dish["difficulty"],
        "techniques": dish["techniques"],
        "critical_techniques": [t for t in dish["techniques"] if t["precision"] == "critical"],
        "temperature_range_c": {
            "min": min(t["temperature_c"] for t in dish["techniques"]),
            "max": max(t["temperature_c"] for t in dish["techniques"]),
        },
    }, indent=2)


@mcp.tool()
def get_safety_requirements(dish_name: str) -> str:
    """
    Get safety considerations for preparing a dish, including temperature
    hazards and handling precautions.

    Args:
        dish_name: Name of the dish
    """
    _, dish = _find_dish(dish_name)
    if dish is None:
        return json.dumps({
            "error": f"Dish '{dish_name}' not found.",
            "available_dishes": list(DISH_DATABASE.keys()),
        }, indent=2)
    return json.dumps({
        "dish": dish["name"],
        "safety_warnings": dish["safety"],
        "max_temperature_c": max(dish["temperatures"].values()),
        "critical_techniques": [
            {"technique": t["name"], "temperature_c": t["temperature_c"]}
            for t in dish["techniques"] if t["precision"] == "critical"
        ],
    }, indent=2)


@mcp.tool()
def get_equipment_specs(equipment_name: str) -> str:
    """
    Get specifications for kitchen equipment including temperatures and usage notes.

    Args:
        equipment_name: Name of the equipment (e.g. 'oven', 'wok', 'deep fryer')
    """
    EQUIPMENT_DB = {
        "oven": {"name": "Commercial Convection Oven", "temperature_range_c": {"min": 50, "max": 300},
                 "power_watts": 5000, "precision_c": 5,
                 "notes": "Preheat at least 20 minutes for accurate temperature."},
        "wok": {"name": "Carbon Steel Wok", "temperature_range_c": {"min": 100, "max": 350},
                "material": "carbon steel",
                "notes": "Reaches very high temperatures. Requires seasoning."},
        "deep fryer": {"name": "Commercial Deep Fryer", "temperature_range_c": {"min": 120, "max": 200},
                       "power_watts": 3500, "precision_c": 2,
                       "notes": "Never exceed 200°C. Monitor oil quality."},
        "electric mixer": {"name": "Stand Mixer", "speed_range_rpm": {"min": 50, "max": 300},
                           "power_watts": 800,
                           "notes": "Ideal for whipping egg whites. Start on low speed."},
        "rice cooker": {"name": "Programmable Rice Cooker", "temperature_range_c": {"min": 60, "max": 105},
                        "precision_c": 1,
                        "notes": "Precise water-to-rice ratio is essential."},
        "dutch oven": {"name": "Cast Iron Dutch Oven", "temperature_range_c": {"min": 100, "max": 260},
                       "capacity_litres": 5.5,
                       "notes": "Preheat in oven for bread baking. Very heavy."},
        "non-stick pan": {"name": "Non-Stick Frying Pan 20cm", "temperature_range_c": {"min": 100, "max": 200},
                          "notes": "Do not exceed 200°C or use metal utensils."},
        "saucepan": {"name": "Stainless Steel Saucepan", "temperature_range_c": {"min": 60, "max": 250},
                     "notes": "Good for béchamel, sauces, and ganache."},
    }
    key = equipment_name.lower().strip()
    equip = EQUIPMENT_DB.get(key)
    if equip is None:
        for k, e in EQUIPMENT_DB.items():
            if key in k or k in key:
                equip = e
                break
    if equip is None:
        return json.dumps({"error": f"Equipment '{equipment_name}' not found.",
                           "available": list(EQUIPMENT_DB.keys())}, indent=2)
    return json.dumps(equip, indent=2)


# ---------------------------------------------------------------------------
# Run as MCP server
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
