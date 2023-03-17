import discord
from transformers import MarianMTModel, MarianTokenizer
import asyncio
from lingua import Language, LanguageDetectorBuilder

# Discord bot initialization
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Language detection initialization
languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

# Emoji initialization
emoji = "🔄"

# Translation initialization
translations = {}

# ---------------------------------------------------------------
async def translateFR_DE(text):
    fr_de_model = 'Helsinki-NLP/opus-mt-fr-de'
    tokenizer = MarianTokenizer.from_pretrained(fr_de_model)
    model = MarianMTModel.from_pretrained(fr_de_model)

    # Tokenize the input text
    inputs = tokenizer(text, return_tensors='pt')

    # Translate the input text using the model
    outputs = model.generate(**inputs, max_length=128, num_beams=4, early_stopping=True)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return translated_text

async def translateDE_FR(text):
    de_fr_model = 'Helsinki-NLP/opus-mt-de-fr'
    tokenizer = MarianTokenizer.from_pretrained(de_fr_model)
    model = MarianMTModel.from_pretrained(de_fr_model)

    # Tokenize the input text
    inputs = tokenizer(text, return_tensors='pt')

    # Translate the input text using the model
    outputs = model.generate(**inputs, max_length=128, num_beams=4, early_stopping=True)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return translated_text

# ---------------------------------------------------------------
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text = message.content
    language = detector.detect_language_of(text)

    if language in [Language.FRENCH, Language.GERMAN]:
        # React with the emoji to the message
        await message.add_reaction(emoji)

        # Check if there is a previous translation for the message
        if message.id in translations:
            translated_text = translations[message.id]
        else:

            if language == Language.FRENCH:
                translated_text = await translateFR_DE(text)
            elif language == Language.GERMAN:
                translated_text = await translateDE_FR(text)

            # Save the translation in the translations dictionary
            translations[message.id] = translated_text


        # Check if the emoji reaction is added by a different user
        def check(reaction, user):
            return user != client.user and str(reaction.emoji) == emoji and reaction.message.id == message.id

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
            if message.id in translations:
                # Reply to the original message with the translation
                await message.reply(translations[message.id])
        except asyncio.TimeoutError:
            pass

    elif language == Language.ENGLISH:
        # If the language is English, do nothing
        pass

client.run('MTA4NjMyNDMxMTcyNTQ0OTI4OA.GI0thp.fZo0hmK81lwVxr_Om8h52lwr3G3vwZCSKEXmB4')
