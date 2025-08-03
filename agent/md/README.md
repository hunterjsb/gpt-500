# MD
markdown. a fuckton of markdown. think of it as the llm's notebook.

### indicies
human/llm-readable output of a given index (like the GPT-20).

### notes
documents used by the agent to store text information. the agent can edit these notes arbitrarily.

### prompts
used to set up agents, static files fed to the llm to induce some sort of behavior.


## naming conventions
uppercased files (e.g. SYSTEM.md) are static and SHOULD NOT be edited by the agent. lowercased files can be freely edited by the agent. some files (e.g. indicies/GPT20.md) can be edited by the agent by not directly, only through editing the underlying data that it is generated from.
