# Train

I've now created my dataset so I'm going to try start finetuning. I'm sure I'll be going back to the data stage before long but hopefully I shall be more informed.

I'm going to use the [axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) library because it looks pretty neat and has some simple examples that I can modify for my use case.

For this I am running the container [`winglian/axolotl-runpod:main-latest`](https://runpod.io/gsc?template=v2ickqhz9s&ref=6i7fkpdz) in runpod as suggested in the README. I'm using this so I can save my pennies:

```
1 x RTX 3090
7 vCPU 30 GB RAM
```

I've decided to start with [this example](https://github.com/OpenAccess-AI-Collective/axolotl/blob/main/examples/mistral/qlora.yml) as it will require minimal changes (I think).

Just have to run this:

```bash
accelerate launch -m axolotl.cli.train qlora.yml
```

Now for inference:

```bash
python -m axolotl.cli.inference qlora.yml --lora_model_dir="./qlora-out" --gradio
```

I've created a simple notebook `get_new_example.ipynb` in order to generate fresh unseen prompts from online recipes in the alpaca style.

## Extras

`get_name.py` is a simple script to generate names for my training runs
