import logging

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
    recipe = get_recipe(url)
    record = {}
    record["instruction"] = INSTRUCTION
    record["input"] = recipe
    prompt = get_alpaca_prompt(record)
    return prompt


def main(url, output_path="recipe-gantt.tsv"):
    logger.info("Loading model...")
    llm = Llama(
        model_path="merged_ggml-model-q4_0.gguf", n_ctx=0, n_gpu_layers=1, verbose=False
    )
    logger.info("Downloading recipe ⬇️")
    prompt = get_prompt(url)
    logger.info("Generating gantt chart...")
    output = llm(prompt, max_tokens=4096, echo=False)
    output = output["choices"][0]["text"]
    with open(output_path, "w") as file:
        file.write(output)
    logger.info(f"Written recipe gantt chart to {output_path}")


if __name__ == "__main__":
    Fire(main)
