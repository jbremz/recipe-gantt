# Train

I've now created my dataset so I'm going to try start finetuning. I'm sure I'll be going back to the data stage before long but hopefully I shall be more informed.

I'm going to use the [axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) library because it looks pretty neat and has some simple examples that I can modify for my use case.

For this I am running the container [`winglian/axolotl-runpod:main-latest`](https://runpod.io/gsc?template=v2ickqhz9s&ref=6i7fkpdz) in runpod as suggested in the README.

I've decided to start with [this example](https://github.com/OpenAccess-AI-Collective/axolotl/blob/main/examples/mistral/qlora.yml) as it will require minimal changes (I think).

```bash
accelerate launch -m axolotl.cli.train qlora.yml
```
