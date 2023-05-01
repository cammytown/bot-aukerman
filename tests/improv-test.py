from bot_aukerman import Performance, HumanPerformer, BotPerformer

verbose = True

if verbose:
    print("Initializing performance...")

# Initialize a performance
# model_config = { "name": "gpt2", }

model_config = {
    "name": "text-ada-001",
    "remote": "openai",
}

# model_config = {
    # "name": "text-ada-001",
    # "remote": "openai",
    # "name": "decapoda-research/llama-7b-hf",
    # "model" = "PygmalionAI/pygmalion-350m"
    # "model" = "gpt2-large"
# },

performance = Performance(#logdir = "logs/bot_aukerman/",
                          model_config = model_config,
                          resume_from_log = False)

if verbose:
    print("Initializing performers...")

# Create human performer
human = HumanPerformer(
    character_name = "Cammy",
)

# Create bot performers
talking_frog = BotPerformer(
    # chatbot=llamacpp_bot,
    character_name="Frog",
    character_desc="A talking frog; extremely intelligent but very sarcastic and patronizing. Flawed character.",
    # model_config = {
    #     "name": "gpt2",
    # },
    # speaker=performance.tts.tts.speakers[2],
)

homeless_man = BotPerformer(
    # chatbot=llamacpp_bot,
    character_name="Homeless Man",
    character_desc="A homeless man; distraught about existential concerns and the state of society. Hates money. Hates capitalism. Refuses to participate.",
    # speaker=performance.tts.tts.speakers[1],
    # model_config = {
    #     "name": "gpt2",
    # },
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
# performance.add_dialogue("FROG:")

# FROG: Hey! Watch where you're sitting!
# HOMELESS MAN: What the!?
# FROG: Yeah, yeah, yeah. A talking frog. Crazy, I know.
# HOMELESS MAN: You— but— how?
# FROG: Let's not get into it right now.
# HOMELESS MAN: Why not?
# FROG: Don't you think every single human I come across wants to talk about the same thing?
# HOMELESS MAN: Well yeah, no shit. You're a talking frog. It's pretty unique.
# FROG: Oh my god just let it go, already.

if verbose:
    print("Generating dialogue...")

performance.start_interactive()

if verbose:
    print("Performing dialogue...")

# Perform the script:
performance.perform()

# Print the model timings:
# performance.chatbot.model.print_timings()

# Print dialogue
# print(performance.working_script)

