verbose = True

if verbose:
    print("Importing modules...")

from bot_aukerman import Performance, HumanPerformer, BotPerformer

if verbose:
    print("Initializing performance...")

# Initialize a performance
# model_config = { "engine": "rwkv" }
model_config = {
    "model": "gpt2-large",
    "use_cuda": True,
    "max_context_length": 768, 
    # "model": "gpt2"
    # "model": "gpt4all-7B-unfiltered", "engine": "llamacpp"
    # "model": "text-ada-001", "engine": "openai",
    # "engine": "openai",
}

performance = Performance(model_config = model_config,
                          resume_from_log = False)

if verbose:
    print("Initializing performers...")

# Create human performer
human = HumanPerformer(
    character_name = "Cammy",
)

# Create bot performers
talking_frog = BotPerformer(
    character_name="Frog",
    character_desc="A talking frog; extremely intelligent but very sarcastic and patronizing. Flawed character.",

    # model_config={ "model": "gpt2-large", },
)

homeless_man = BotPerformer(
    character_name="Homeless Man",
    character_desc="A homeless man; distraught about existential concerns and the state of society. Hates money. Hates capitalism. Refuses to participate.",

    # model_config={ "model": "text-ada-001", "engine": "openai" },
)

if verbose:
    print("Adding performers to performance...")

# Add characters to performance
performance.add_performer(human)
performance.add_performer(talking_frog)
performance.add_performer(homeless_man)

# Add setting description to performance
performance.set_scene("EXT. A PUBLIC PARK - DAY")

# Add some action description to the performance
performance.add_description("An odd blue FROG is sitting on a bench. A HOMELESS MAN comes walking by, looking glum.")

performance.add_dialogue("FROG: Well, well, well, hello there mister human.")
performance.add_dialogue("HOMELESS MAN: Huh? Who are you?")
performance.add_dialogue("FROG: Isn't it obvious?")
performance.add_dialogue("HOMELESS MAN: A… a frog?")
performance.add_dialogue("FROG: That's right.")
performance.add_dialogue("HOMELESS MAN: But… but how?")

# performance.add_dialogue("FROG: Hey! Watch where you're sitting!")
# performance.add_dialogue("HOMELESS MAN: What the!?")
# performance.add_dialogue("FROG: Yeah, yeah, yeah. A talking frog. Crazy, I know.")
# performance.add_dialogue("HOMELESS MAN: You— but— how?")
# performance.add_dialogue("FROG: Let's not get into it right now.")
# performance.add_dialogue("HOMELESS MAN: Why not?")
# performance.add_dialogue("FROG: Don't you think every single human I come across wants to talk about the same thing?")
# performance.add_dialogue("HOMELESS MAN: Well yeah, no shit. You're a talking frog. It's pretty unique.")
# performance.add_dialogue("FROG: Oh my god just let it go, already.")

if verbose:
    print("Starting interactive performance...")

performance.start_interactive_text()

if verbose:
    print("Performing dialogue...")

# Perform the script:
# performance.perform()

# Print the model timings:
# performance.chatbot.model.print_timings()

# Print dialogue
# print(performance.working_script)

