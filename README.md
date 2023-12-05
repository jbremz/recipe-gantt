# Recipe Gantt 🧑‍🍳

The idea is this:

- Take a typical recipe (one that you might find online) with standard Ingredients and Method sections
- Use an LLM to convert it into a Gantt chart (in this case a table) with:
  - the individual steps in the method as columns
  - the individual ingredients as rows
  - an "X" in each cell corresponding to the steps where that ingredient is used

The hope is this would provide a simpler graphical way of viewing complicated recipes without having to move back and forth between the ingredients and the method inefficiently.

It's very overengineered.

## The development plan

1. Use GPT4 assistant to make a first pass training dataset. It performs ok, but still makes mistakes and produces inconsistently formatted tables.
1. Manually fix any mistakes in this dataset
1. Finetune an open-source model on the dataset
