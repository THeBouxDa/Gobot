from discord import Intents

def personalized() -> Intents:
    intents = Intents.default()
    intents.typing = False
    intents.presences = False
    intents.message_content = True
    intents.members = True
    
    return intents
