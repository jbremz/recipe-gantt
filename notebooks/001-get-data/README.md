# Dataset

So I need to:

1. Collect some recipe URLs - I used [this](https://github.com/fictivekin/openrecipes) dataset
1. Format them consistently (hopefully that will help the model focus on the important actions) - I used [this](https://github.com/hhursev/recipe-scrapers) handy recipe scraping tool
1. Send them to GPT4 assistant via API and collect resulting .tsv files
1. Manually inspect results and modify/remove any noisy examples

There will be data loss at each of these stages but I hope I'm left with enough to finetune a half-decent model! If dataset size is an issue I reckon I can break the task down into producing individual columns of the table _or_ even individual cells. There are downsides to this though.
