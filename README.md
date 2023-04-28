Under heavy development.

# TODO
## cases to handle
- sometimes you get things like CHARACTER ONE: CHARACTER TWO: [dialogue]
    - maybe only use last character name
- tendency of certain models to put \n after character name / before dialogue
    - decrease likelihood of \n token?
- scene headers

## chatbots
- accept parameters that determine chatbot parameters like temperature in a way that is abstracted away from the behavior of specific chatbots such that users can specify parameters like "incoherence/creativity" and have it get mapped to specific parameters for specific LLM models

## BOT PERFORMANCES
- ways to suggest that the characters do or say particular things or behave in particular ways during the course of a performance
- other things to track within Performer (mood, conflict, inventory)?

# Getting good language model output
For less "intelligent" language models like GPT2, the initial setup is
important and delicate.

For instance:

```fountain
FROG
Well, well, well, hello there mister human.

MAN
Huh? Who are you?

FROG
Isn't it obvious?

MAN
A… a frog?

FROG
That's right.

MAN
But… but how?
```

Repetition of any kind seems to cause problems. The model might try to reprise
the phrase "Well, well, well", but won't know where to stop. This will slowly
inspire other characters to behave similarly; like a mind virus.

# NOTES / POINTS OF INTEREST
- Named after Scott Aukerman as a tribute to his legendary work hosting legendary improvisational comedy show **Comedy Bang! Bang!**.
