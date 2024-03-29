# Recipe Gantt 🧑‍🍳

Recipe Gantt uses an LM to automatically convert recipes like [this one](https://www.bbcgoodfood.com/recipes/next-level-banoffee-pie) 🍌 into gantt charts like the one below:
![Next level banoffee pie](assets/next-level-banoffee-pie-gantt.png "Next level banoffee pie")

The hope is to provide a simpler graphical way of viewing recipes (especially complicated multi-step ones) without having to move back and forth between the ingredients and the method inefficiently.

It's very over-engineered.

## Installation

```bash
conda env create -f env.yml 
```

**NOTE:** I have only tested this on my 2021 Macbook Pro (with M1 Pro). There's every possibility that llama.cpp will behave differently for other systems.

## Usage

First, activate the conda environment:

```bash
conda activate recipe-gantt
```

Then you can run the CLI:

```bash
python recipe-gantt.py
```

**NOTE:** the first time you run this script it will download the model (4.11GB) to your local huggingface cache.

## Development process

### Data collection

1. Used the [openrecipes](https://github.com/fictivekin/openrecipes) dataset to get a few hundred recipe URLs
2. Used [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) library to extract the ingredients and method steps when given a recipe URL ([code](https://github.com/jbremz/recipe-gantt/blob/1c37b115b155a128e0765040197c5783b5a91ff3/notebooks/001-get-data/02-save-recipes.ipynb)).
3. A custom GPT Assistant was written to generate the desired gantt charts as TSV files (albeit much more slowly and expensively) from simplified Ingredients, Method formatted recipes ([code](https://github.com/jbremz/recipe-gantt/blob/1c37b115b155a128e0765040197c5783b5a91ff3/notebooks/001-get-data/03-query-gpt4.ipynb)).  A publicly accessible GPT version of the same assistant is [here](https://chat.openai.com/g/g-VG5s6fStY-recipe-gantt).
4. Did a small amount of manual tweaking of the outputs to improve data quality before I lost my mind and moved on ([code](https://github.com/jbremz/recipe-gantt/blob/1c37b115b155a128e0765040197c5783b5a91ff3/notebooks/001-get-data/04-check-results.ipynb)).

You can find the dataset hosted here: [pocasrocas/recipe-gantt](https://huggingface.co/datasets/pocasrocas/recipe-gantt).

### Finetuning/implementation

1. Used [axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) to do a QLoRA fine-tune of Mistral-7B-v0.1 on this dataset of 288 examples of (recipe input, gantt chart output) pairs. This model wouldn't need the tedious CoT prompting that I had to use with GPT4 and instead could map directly to the output, making it ~4x quicker. I could also host it locally which was better than paying for GPT4 credits ([code](https://github.com/jbremz/recipe-gantt/tree/002-train/notebooks/002-train)).
2. Made use of [llama.cpp](https://github.com/ggerganov/llama.cpp) and [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) to compress the finetuned model and run it locally on my macbook at ~30tok/s

You can see the wandb training logs [here](https://wandb.ai/pocasrocas/recipe-gantt/runs/1ostj66y/workspace).

The resulting model is hosted here: [pocasrocas/recipe-gantt-v0.1](https://huggingface.co/pocasrocas/recipe-gantt-v0.1) (but it will be automatically downloaded the first time you run the script).

## Areas for future development

1. It's not pretty, but then frontend isn't really my thing... any PRs to give this a proper UI etc. are very welcome
2. It surprised me how little data was required to produce a good-quality model. However, sometimes it produces corrupted TSV files or populates the cells inaccurately. The simplest answer would be to scale up the finetuning data from \~100s to e.g. 1000s of samples. This would be very straightforward to do but I didn't feel like spending more than I already had done (\~£20) on OpenAI credits...
3. There are potentially more intelligent ways of constraining the model outputs to valid TSV 🤔
4. My alpaca prompting strategy feels inefficient. Given this is a mono-task LM, each prompt is largely the same except for a different input appended to the end. Given enough finetuning data, the model should be able to learn the task without needing the same preamble every time. Perhaps one could start with a model finetuned on the whole prompt and then switch to removing it later. This should save on redundant computation and allow shorter context lengths.
5. The recipe-scrapers library sometimes fails and unfortunately doesn't support all of the recipe websites that I have tried (you can find a list of supported sites [here](https://github.com/hhursev/recipe-scrapers?tab=readme-ov-file#scrapers-available-for)). This could make things frustrating for practical use but I'm not sure if I'm motivated enough to contribute more scrapers to that project. I did play around with learning a mapping from raw HTML to the gantt chart but it would have required a much larger context length and probably a larger finetuning set (due to greater variability in the input).
6. This task is quite straightforward and I'm not sure if we need all of Mistral's 7B parameters (especially in the monotask setting)... It might be interesting to try much smaller models. Then again, I'm not sure whether we'd need to increase the dataset size accordingly.
7. These "Gantt charts" aren't _strictly_ Gantt charts 🤫 (although I'd say they are in spirit). What would be cooler would be a more general recipe Gantt chart generator that could address common supra-ingredient annoyances e.g. when you're told to preheat the oven but only at the point you need the oven preheated 😒. The rows of this Gantt chart could then be divided into ingredient and general prep rows perhaps. One might also then want to create some kind of time axis (as opposed to working in time units of method steps). This would require more advanced reasoning from the LM but feels totally within reach.
