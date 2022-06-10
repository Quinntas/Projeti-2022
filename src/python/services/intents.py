import json


class IntentRecognizer(object):
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.bad_words = self.config['bad_words']
        self.completion_phrases = self.config['completion_phrases']
        self.bad_phrases = self.create_phrases()

    @staticmethod
    def load_config(config_path: str) -> dict:
        with open(config_path, "r") as f:
            return json.load(f)

    def create_phrases(self) -> list:
        phrases = []
        for completion_phrase in self.completion_phrases:
            for bad_word in self.bad_words:
                phrases.append(completion_phrase + " " + bad_word)
        return phrases

    def recognize_phrase(self, text: str) -> int:
        worry_score = 0

        for phrase in self.bad_phrases:
            if phrase == text or phrase in text:
                worry_score += 1

        for word in text.split():
            if word in self.bad_words:
                worry_score += 1

        return worry_score

    @staticmethod
    def clean_text(text: str) -> str:
        return text.replace(",", "").replace(".", "")

    def recognize_text(self, text: str) -> int:
        return self.recognize_phrase(self.clean_text(text))
