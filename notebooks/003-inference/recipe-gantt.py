import logging
from io import StringIO

import pandas as pd
import plotly.graph_objects as go
from fire import Fire
from llama_cpp import Llama

from recipe_gantt.data import INSTRUCTION, get_alpaca_prompt, get_recipe

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
c_format = logging.Formatter("🧑‍🍳 RECIPE GANTT: %(message)s")
c_handler.setFormatter(c_format)

logger.addHandler(c_handler)


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
    return pd.read_csv(StringIO(output), sep="\t")


def plot_gantt(df, figsize=(1000, 2000)):
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


def main(output_path="recipe-gantt.tsv", display=True):
    logger.info("Loading model...")
    llm = Llama(
        model_path="merged_ggml-model-q4_0.gguf", n_ctx=0, n_gpu_layers=1, verbose=False
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
        df = read_tsv(output)
        plot_gantt(df)


if __name__ == "__main__":
    Fire(main)
