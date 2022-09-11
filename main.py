from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import (
    Union, List
)
import json
import random
import regex

app = FastAPI()

origins = [
    "*"
]

class Recipe(BaseModel):
    title: str
    time: Union[str, None] = None
    ingredients: List[str]
    steps: List[str]

class Ingredient:
    def __init__(self, quantity: str, measurement: str, item: str):
        self.quantity = quantity
        self.measurement = measurement
        self.item = item

class DeleteBody(BaseModel):
    recipe: Recipe
    store: List[Recipe]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_random_recipe():
    f = open('data.json')
    data = json.load(f)
    recipes = data["recipes"]
    rand = random.randint(0, len(recipes)-1)
    
    return recipes[rand]

def get_ingredient_quantity(ingredient):
    quantity = regex.search("^\\d*[^a-zA-Z \\*]?\\d*", ingredient)
    if quantity is None:
        return ""
    else:
        return quantity.group()

def get_ingredient_measurement(ingredient):
    measurement = regex.search("tbsps?|tsps?|cups?|cans?|packages?|packets?|ozs?|pounds?", ingredient)

    if measurement is None:
        return ""
    else:
        return measurement.group()

def get_ingredient_item(ingredient):
    if get_ingredient_measurement(ingredient) == "":
        item = regex.search("\\*?[a-zA-Z].*", ingredient)
    else:
        item = regex.search("(?<=tbsps? |tsps? |cups? |cans? |packages? |packets? |ozs? |pounds? )\\*?[a-zA-Z].*", ingredient)
    return item.group()

def class_ingredients(ingredients):
    ret = []
    for ingredient in ingredients:
        quantity = get_ingredient_quantity(ingredient)
        measurement = get_ingredient_measurement(ingredient)
        item = get_ingredient_item(ingredient)
        ret.append(Ingredient(quantity, measurement, item))

    return ret

def alphabetize_ingredients(ingredients):
    ingredients.sort(key=lambda x: x.item.lower())
    return ingredients

def combine_ingredients(ingredients):
    print("max: " + str(len(ingredients)-1))
    i = 0
    max = len(ingredients) - 2
    while i < max:
        j = i + 1
        print("i: " + str(i))
        if ingredients[i].item in ingredients[j].item or ingredients[j].item in ingredients[i].item:
            if ingredients[i].measurement in ingredients[j].measurement or ingredients[j].measurement in ingredients[i].measurement:
                if ingredients[i].quantity != "":
                    if len(ingredients[i].item) > len(ingredients[j].item):
                        ingredients[i].item = ingredients[j].item
                    
                    if len(ingredients[i].measurement) > len(ingredients[j].measurement):
                        ingredients[i].measurement = ingredients[j].measurement

                    if "." in ingredients[i].quantity or "." in ingredients[j].quantity: 
                        ingredients[i].quantity = str(float("{:.2f}".format(float(ingredients[i].quantity) + float(ingredients[j].quantity))))
                    else:
                        ingredients[i].quantity = str(int(ingredients[i].quantity) + int(ingredients[j].quantity))
                
                ingredients.remove(ingredients[j])
                i = i - 1
                max = max - 1
        i = i + 1
    return ingredients


@app.get("/")
async def root():
    return "Root."

@app.get("/random")
async def random_recipe(num: int = 1):
    ret = []

    for i in range(num):
        recipe = get_random_recipe()
        ret.append(recipe)
    
    return ret

@app.get("/recipes")
async def filter(filter: str = "*", min: int = 0, max: int = 50):
    f = open('data.json')

    data = json.load(f)
    recipes = data["recipes"]

    ret = []

    for recipe in recipes:
        title = recipe.get("title")
        # Account for recipes without a cooking time specified
        recipe_time = regex.findall(r'\d+', recipe.get("time"))
        if recipe_time != []:
            recipe_time = int(recipe_time[0])

        # If the filter is in the recipe title
        if filter.lower() in title.lower() or filter == "*":
            if recipe_time != []:
                if min <= recipe_time <= max:
                    ret.append(recipe)
            else:
                ret.append(recipe)
    
    return ret

@app.delete("/delete")
async def delete(body: DeleteBody):
    store = body.store
    store.remove(body.recipe)

    return store

@app.post("/ingredients")
async def ingredients(body: List[Recipe]):
    ingredientsList = []
    for recipe in body:
        for ingredient in recipe.ingredients:
            ingredientsList.append(ingredient)

    ingredientsList = class_ingredients(ingredientsList)
    ingredientsList = alphabetize_ingredients(ingredientsList)
    ingredientsList = combine_ingredients(ingredientsList)

    return ingredientsList
