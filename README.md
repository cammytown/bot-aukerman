# TODO
- cases to handle
    - sometimes you get things like CHARACTER ONE: CHARACTER TWO: [dialogue]
        - maybe only use last character name
    - tendency of certain models to put \n after character name / before dialogue
        - decrease likelihood of \n token?
- (optionally) abstract away the initialization of chatbots; consider a secondary library/module that does this
    - as part of this, it should accept parameters that determine chatbot parameters like temperature in a way that is abstracted away from the behavior of specific chatbots such that users can specify parameters like "incoherence/creativity" and have it get mapped to specific parameters for specific LLM models

## BOT PERFORMANCES
- ways to suggest that the characters do or say particular things or behave in particular ways during the course of a performance
- other things to track within Performer (mood, conflict, state)?
