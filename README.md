Under heavy development.

# Development Setup
## The following packages currently must be installed separately, for now.

```
"llmber @ git+https://github.com/cammytown/llmber.git",
"vosk_imp @ git+https://github.com/cammytown/vosk-imp.git",
"coqui_imp @ git+https://github.com/cammytown/coqui-imp.git",
```

```shell
cd bot-aukerman/

# Optionally create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```


# Roadmap
1. Basic groundwork
1. User interface

# Notes / Points of Interest
- Named after Scott Aukerman; hope he doesn't do something weird and get cancelled or we'll have to rename this package.
- Taking psychedelic drugs can improve LLM output.
