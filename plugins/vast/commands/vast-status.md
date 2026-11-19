---
description: Show what is running on Vast.ai, what it has cost so far, and how many hours each price band has left this fortnight
---
Call the vast server's `instances` tool, then report one short table of instances (id, GPU, status, $/hr, hours run, hours left, and a flag for anything over its deadline or not in the ledger), and one of price bands (budget, counted, remaining), both taken from the result's `spend` block.

Do not rent, stop, destroy or reap anything from this command. If something is over its deadline, say so and offer `reap` as a dry run.
