import os

COMMAND_IDS = {
    "send": os.getenv("DISCORD_COMMAND_ID_SEND"),
    "feedback": os.getenv("DISCORD_COMMAND_ID_FEEDBACK")
}