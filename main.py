from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import re

app = FastAPI()

origins = [
    "*"
]

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

@app.get("/")
async def root():
    return "Bitches."

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
        recipe_time = re.findall(r'\d+', recipe.get("time"))
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