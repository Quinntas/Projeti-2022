import json


class IntentRecognizer(object):
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.bad_words = self.config['bad_words']

    @staticmethod
    def load_config(config_path: str) -> dict:
        with open(config_path, "r") as f:
            return json.load(f)

    def recognize_text(self, text: str) -> int:
        worry_score = 0

        for word in text.split():
            if word in self.bad_words:
                worry_score += 1

        return worry_score
