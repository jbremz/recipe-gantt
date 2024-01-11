from recipe_scrapers import scrape_me


def extract_ingredients_and_steps(scraper):
    """
    Extracts the ingredients and steps from a recipe scraper object.

    Args:
        scraper: The recipe scraper object.

    Returns:
        A tuple containing the ingredients and steps as separate lists.
    """
    recipe_dict = scraper.to_json()

    ingredients = recipe_dict["ingredients"]

    instructions = recipe_dict["instructions_list"]
    if len(instructions) == 1:  # the method split didn't work
        instructions = instructions[0].split(".")
        instructions = [i.strip() + "." for i in instructions]
        instructions = [i for i in instructions if i != "."]

    return ingredients, instructions


def format_recipe(ingredients, instructions):
    """
    Formats the given ingredients and instructions into a readable recipe format.

    Args:
        ingredients (list): A list of ingredients.
        instructions (list): A list of instructions.

    Returns:
        str: The formatted recipe text.
    """
    formatted_text = "Ingredients\n\n"
    for ingredient in ingredients:
        formatted_text += ingredient + "\n"

    formatted_text += "\nMethod\n\n"
    for i, step in enumerate(instructions):
        formatted_text += f"{i+1}. {step}\n"

    return formatted_text


def get_recipe(url):
    """
    Retrieves a recipe from the given URL and returns it in a formatted way.

    Args:
        url (str): The URL of the recipe to retrieve.

    Returns:
        str: The formatted recipe.

    """
    scraper = scrape_me(url)
    ingredients, instructions = extract_ingredients_and_steps(scraper)
    return format_recipe(ingredients, instructions)


def get_alpaca_prompt(record):
    return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{record['instruction']}

### Input:
{record['input']}

### Response:"""
