from elevenlabs import generate, play, set_api_key, voices
from pydub import AudioSegment
import argparse
import requests
import openai
import io
import os


def main():

    # Description of the program
    description = 'Text to speech bot for Magic: The Gathering cards.'

    # Parse the arguments from the command line
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', type=str, help='Card name.')
    parser.add_argument('-s', type=str, help='Unique set code.')
    parser.add_argument('-p', type=str, help='Path to prompt.txt file. (optional)', default='prompt.txt')
    parser.add_argument('-o', type=str, help='Path to output the audio file. (optional)')
    parser.add_argument('--format', type=str, help='Audio format to output. (optional)', default='mp3')
    parser.add_argument('--stream', action='store_true', help='Stream the audio')
    parser.add_argument('-t', action='store_true', help='Output the script to standard output.')
    args = parser.parse_args()

    # Import the necessary API keys
    openai.api_key = os.environ.get('OPEN_AI_KEY')
    set_api_key(os.environ.get('ELEVEN_LABS_KEY'))

    # Define the endpoint to the Scryfall API
    scryfall_url = f"https://api.scryfall.com/cards/named?fuzzy={args.c}"

    # If the optional arg set is given add it to the URL
    if (args.s):
        scryfall_url += f"&set={args.s}"

    # Send the GET request to the Scryfall API 
    response = requests.get(scryfall_url)
    data = response.json()

    # Define the metadata to extract from the card object
    metadata = ['name',
                'type_line',
                'mana_cost',
                'oracle_text',
                'loyalty',
                'power',
                'toughness']

    card_info = ''

    # If card is double sided
    if 'card_faces' in data:
        for face in data['card_faces']:
            for i in metadata:
                if (i in face):
                    card_info += f'{i}: {face[i]} '
    # If card is single sided
    else:
        for i in metadata:
            if (i in data):
                    card_info += f'{i}: {data[i]} '

    # Prompt the mtg-card-bot
    with open(args.p, 'r') as file:
        prompt = file.read()

    # Set the model
    model = "gpt-3.5-turbo"

    # Curate the response
    response = openai.ChatCompletion.create(
    model = model,
    messages = [{"role": "system", "content": prompt},
                {"role": "user", "content": card_info}]
    )

    
    # Store response as variable
    card_info = response.choices[0]['message']['content']

    # Generate the audio
    audio = generate(text=card_info, voice="Josh")

    # Output to file
    if (args.o):
        # Output the generate audio file
        audio_file = AudioSegment.from_file(io.BytesIO(audio), format='mp3')
        audio_file.export(f"{args.o}", format='mp3')

    # Output response text 
    if (args.t):
        print(response.choices[0]['message']['content'])

    if (args.stream):
        play(audio)
        

if __name__ == '__main__':
    main()
