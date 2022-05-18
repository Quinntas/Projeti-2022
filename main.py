import os

from dotenv import load_dotenv

from src.python.services.intents import IntentRecognizer

__app_name__ = "VoiceFY"
__description__ = "UM ALGORITMO QUE FAZ O RECONHECIMENTO DA INTENÇÃO, HUMOR E EMOÇÃO ATRAVÉS DE FALA " \
                  "PARA A SEGURANÇA DA MULHER"
__version__ = 0.1
__license__ = "MIT"
__author__ = ["Caio Quintas", "Ana Carolina", "Arnold Brito", "Luiz Eduardo", "William Kelvem"]
__author_email__ = ["caioquintassantiago@gmail.com"]

load_dotenv()
GOOGLE_AUDIO_RECOGNIZER_API = os.environ.get("GOOGLE_AUDIO_RECOGNIZER_API")


def main():
    # listener = Listener(GOOGLE_AUDIO_RECOGNIZER_API)
    intent_recognizer = IntentRecognizer("data/intents.json")

    score = intent_recognizer.recognize_text("eu vou te matar sua vaca")
    if score > 3:
        print("ALERT")


if __name__ == "__main__":
    main()
