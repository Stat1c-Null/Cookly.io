# pip install -U sentence-transformers
# You will probably need to install the rest too but using google collab i believe it comes with those
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import torch
import ast
import re
import json
import os

device = 'cuda' if torch.cuda.is_available() else 'cpu'
#print(torch.cuda.is_available())

#Will need to change this to the actual place that the csv is saved to
csv_path = "RecipeNLG_enriched.csv"

model = SentenceTransformer('msmarco-MiniLM-L-12-v3', device=device)
#Will need to change this to the actual place that the model is saved to
recipe_embeddings = torch.load("SBertModel.pt", map_location=device)
df = pd.read_csv(csv_path)

recipe_store = {"title": None, "ingredients": None, "directions": None, "link": None}

# Preprocess user input into a set for the Jaccard similarity equation
def parse_ingredients(text):
    return set(ing.strip().lower() for ing in text.split(',') if ing.strip())

def get_recipe():
    print("Sending recipe")
    print(recipe_store.get("title"))
    print(recipe_store.get("ingredients"))
    print(recipe_store.get("directions"))
    print(recipe_store.get("link"))
    return recipe_store.get("title") ,recipe_store.get("ingredients"), recipe_store.get("directions"), recipe_store.get("link")

# Compute Jaccard similarity between user ingredients and recipe ingredients
# Jaccard similarity uses the similarity between two sets by calculating the ratio of the common elements
# 0 is no similarity to 1 being exactly the same
def get_ingredient_overlap_score(ner_ingredients, user_ingredients):
    try:
        recipe_set = set(ast.literal_eval(ner_ingredients))
        user_set = set(ing.lower().strip() for ing in user_ingredients)

        intersection = recipe_set & user_set
        union = recipe_set | user_set

        overlap_score = len(intersection) / len(union) if union else 0.0
        penalty = len(recipe_set - user_set)
        return overlap_score, penalty
    except:
        return 0.0, 0


# Search function
def search_recipes(user_input, top_k=5, length_weight=0.12, ingredient_weight=0.45, penalty_weight=0.02, top_n=200):
    '''
    user_input : a string of all the ingredients the user wants to find a recipe for
    top_k : How many recipes you want to print out
    length_weight : How much the length of the recipe should influence the score
    ingredient_weight : How much should the correct ingredients help the score
    penalty_weight : How much to penalize for missing ingredients
    top_n : How many recipes you want the model to look at to find a match
    '''
    user_ingredients = parse_ingredients(user_input)
    query_embedding = model.encode(user_input, convert_to_tensor=True, device=device)
    scores = util.cos_sim(query_embedding, recipe_embeddings)[0].cpu().numpy()
    top_indices = np.argpartition(scores, -top_n)[-top_n:]

    combined_scores = []
    for i in top_indices:
        row = df.iloc[i]
        base_score = scores[i]
        length_boost = row['length_score'] * length_weight
        ing_score, penalty_count = get_ingredient_overlap_score(row['NER'], user_ingredients)
        ing_boost = ing_score * ingredient_weight
        penalty_boost = -penalty_count * penalty_weight
        combined = base_score + length_boost + ing_boost + penalty_boost
        combined_scores.append((i, combined, ing_score, penalty_count))

    # Sort
    combined_scores.sort(key=lambda x: x[1], reverse=True)

    print(f"\n🔎 Top {top_k} recipe matches for: '{user_input}'")
    for idx, score, ing_score, penalty_count in combined_scores[:top_k]:
        row = df.iloc[idx]
        title = row['title']
        ingredients = row['ingredients']
        directions = row['directions']
        length = row['directions_length']
        link = row['link']
        print(
            f"🍽️ [{link}]{title} — Score: {score:.4f} | Match: {ing_score:.2f} | Penalty: -{penalty_count} | Word Length: {length}")
        print(f"🧂 Ingredients: {ingredients}")
        print(f"📝 Directions: {directions}\n")
        recipe_store["title"] = row['title']
        recipe_store["ingredients"] = row['ingredients']
        recipe_store["directions"] = row['directions']
        recipe_store["link"] = row['link']

    data = {"success": "it just works"}
    return data

#Helper function to see how some of the recipes suck and have bad directions
def findRecipeByIndex(index):
    title = df.iloc[index]['title']
    ingredients = df.iloc[index]['ingredients']
    directions = df.iloc[index]['directions']
    print(f"🍽️ {title}")
    print(f"🧂 Ingredients: {formatDirections(ingredients)}")
    print(f"📝 Directions: {formatDirections(directions)}\n")
    recipe_store["title"] = title
    recipe_store["ingredients"] = ingredients
    recipe_store["directions"] = directions
    recipe_store["link"] = df.iloc[index]['link']

#This is old code to format the directions and I can still use it but I haven't used it in the main search_recipes yet
def formatDirections(directions):
    try:
        steps = ast.literal_eval(directions) if isinstance(directions, str) else directions
        return '\n'.join(step.strip() for step in steps if step.strip())
    except Exception as e:
        print("Error parsing directions:", e)
        return str(directions)


# Run a test search
# eggs, pasta sauce, ground beef, garlic, garlic seasoning, pepper, green pepper, salt, vegetable oil
#userInput = input("Enter ingredients that you have: ")
#search_recipes(userInput, top_k=1, length_weight=0.34, ingredient_weight=0.45, top_n=500)

# findRecipeByIndex(272552)
# print(repr(df.iloc[272552]['directions']))


