Under heavy development.

# Todo / Ideas / Roadmap
- move these into Github issues
- features
    - add characters during performance; esp. automatically from dialogue introducing new characters
    - editable working script during performance to adjust context (will require some slightly complex architecture… set global context state index to point of edit and beyond)
- improving LLM output
    - decrease likelihood of \n token?
    - repetition penalty when implemented in llmber
- improve processing
    - intent parsing of phrases; use to improve functionality (i.e. determine next speaker, add characters dynamically, etc.)
    - consider trying to detect where punctuation marks go to assist LLM in understanding intention (and to improve output script quality)
    - allow option of having character-specific initialization dialogue scripts (i.e. example scripts) that get fed only to chatbot associated with that character
- improving codebase
    - maybe refactor Generator so we don't rely on a classmethod that instantiates a class and so we can move some things like chatbots[] and chatbot_states[] into it; but would require tighter coupling of classes and thus perhaps an intermediate handler class (maybe just called 'BotAukerman')
- improving usability
    - properly incorporate TTS in a way suitable for a public package
    - an interface (separate package?)
    - a way to signal things; like telling a chatbot to reset its context if it starts repeating itself, or to send commands like choosing the next performer, interrupting speech or text generation, and maybe broader things like signaling moods
        - a drama button/signal that tells the LLM(s) to introduce a dramatic/surprising event
        - custom signals
    - properly expose API/configurability for OpenAI/etc. api key setup
    - documentation

## chatbots
- accept abstract parameters that determine chatbot parameters (temperature/etc.) and interaction like "incoherence/creativity/madness" or some such things and have them get mapped to specific parameters/flags for specific LLM models that are used to help influence behavior in more complex/nuanced ways

## bot performances
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

# Notes / Points of Interest
- Named after comedy legend Scott Aukerman; hope he doesn't do something weird and get cancelled or we'll have to rename this package.
