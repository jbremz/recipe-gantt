import logging
from io import StringIO

import pandas as pd
import plotly.graph_objects as go
from fire import Fire
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from recipe_scrapers import scrape_me

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
c_format = logging.Formatter("🧑‍🍳 RECIPE GANTT: %(message)s")
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)
logger.propagate = False

MODEL = hf_hub_download(
    repo_id="pocasrocas/recipe-gantt-v0.1", filename="recipe-gantt-v0.1-q4_0.gguf"
)

INSTRUCTION = """Your task is to transform cooking recipes from raw text into a Gantt chart .tsv file which conveys all the same information but graphically so one can see which ingredients are involved in each step. In the end, we wish to produce a downloadable .tsv file containing a table. It will be structured as follows:

- the column headers will contain the full text description of each step in the recipe (verbatim as in the original recipe)
- Each row will refer to a different ingredient
- If a particular ingredient is used in a particular method step then the corresponding cell is marked with an “X” otherwise it’s left blank

Tip: It's very important that you break down every single ingredient verbatim (with any preparation information - no changes!) as a separate row and copy the method descriptions and verbatim (without making any changes!) from each step to each column header.

Here’s an example:

```
Ingredients

vegetable oil
2 large free-range eggs
100 g plain flour
100 ml milk

Method

1. Preheat the oven to 225°C/425°F/gas 9.
2. Get yourself a cupcake tin and add a tiny splash of vegetable oil into each of the 12 compartments.
3. Pop into the oven for 10 to 15 minutes so the oil gets really hot.
4. Meanwhile, beat the eggs, flour, milk and a pinch of salt and pepper together in a jug until light and smooth.
5. Carefully remove the tray from the oven, then confidently pour the batter evenly into the compartments.
6. Pop the tray back in the oven to cook for 12 to 15 minutes, or until risen and golden.
```

would output this tsv file:
```
Preheat the oven to 225°C/425°F/gas 9.	Get yourself a cupcake tin and add a tiny splash of vegetable oil into each of the 12 compartments.	Pop into the oven for 10 to 15 minutes so the oil gets really hot.	Meanwhile, beat the eggs, flour, milk and a pinch of salt and pepper together in a jug until light and smooth.	Carefully remove the tray from the oven, then confidently pour the batter evenly into the compartments.	Pop the tray back in the oven to cook for 12 to 15 minutes, or until risen and golden.
vegetable oil		X	X		X	X
2 large free-range eggs				X	X	X
100 g plain flour				X	X	X
100 ml milk				X	X	X
```"""


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
    try:
        scraper = scrape_me(url)
    except TypeError:
        raise ValueError(
            "Invalid URL. Most likely this recipe site is not yet supported. Please see https://github.com/hhursev/recipe-scrapers?tab=readme-ov-file#scrapers-available-for for a list of supported sites."
        )
    ingredients, instructions = extract_ingredients_and_steps(scraper)
    return format_recipe(ingredients, instructions)


def get_alpaca_prompt(record):
    return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{record['instruction']}

### Input:
{record['input']}

### Response:"""


def get_prompt(url):
    """
    Retrieves a prompt for generating text based on a given URL.

    Args:
        url (str): The URL of the recipe.

    Returns:
        str: The generated prompt for text generation.
    """
    recipe = get_recipe(url)
    record = {}
    record["instruction"] = INSTRUCTION
    record["input"] = recipe
    prompt = get_alpaca_prompt(record)
    return prompt


def read_tsv(output):
    """
    Read a tab-separated values (TSV) file from a string and return a pandas DataFrame.

    Parameters:
    output (str): The TSV file content as a string.

    Returns:
    pandas.DataFrame: The DataFrame containing the parsed TSV data.
    """
    return pd.read_csv(StringIO(output), sep="\t")


def plot_gantt(df, figsize=(1000, 1800)):
    """
    Plot a Gantt chart using the provided DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data to be plotted.
        figsize (tuple, optional): The size of the figure in pixels. Defaults to (1500, 2000).
    """
    pdf = df.fillna("")
    pdf = pdf.replace("X", "✓")

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(pdf.columns), fill_color="blanchedalmond", align="left"
                ),
                cells=dict(
                    values=[pdf[col] for col in pdf.columns],
                    fill_color="floralwhite",
                    align="center",
                ),
            )
        ]
    )

    fig.update_layout(autosize=False, width=figsize[0], height=figsize[1])

    fig.show()


def main(
    output_path="recipe-gantt.tsv",
    display=True,
    model_path=MODEL,
):
    logger.info("Loading model...")
    llm = Llama(
        model_path=model_path,
        n_ctx=0,  # default length which I think is 8192
        n_gpu_layers=1,  # use M1 metal
        verbose=False,
    )
    url = input("🧑‍🍳 Please enter the recipe URL: ")
    logger.info("Downloading recipe ⬇️")
    prompt = get_prompt(url)

    logger.info("Generating gantt chart...")
    output = llm(prompt, max_tokens=4096, echo=False)
    output = output["choices"][0]["text"]

    with open(output_path, "w") as file:
        file.write(output)
    logger.info(f"Written recipe gantt chart to {output_path}")

    if display:
        logger.info("Opening gantt chart for display 🖥️")
        df = read_tsv(output)
        plot_gantt(df)


if __name__ == "__main__":
    Fire(main)
