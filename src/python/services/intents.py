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
                phrase = completion_phrase['phrase'] + " " + bad_word['word']
                score = completion_phrase['score'] + bad_word['score']
                temp = {"phrase": phrase, "score": score}
                if "alt" in bad_word.keys():
                    temp['alt'] = []
                    for alt in bad_word['alt']:
                        temp['alt'].append(completion_phrase['phrase'] + " " + alt)
                phrases.append(temp)
        return phrases

    def recognize_phrase(self, text: str) -> int:
        worry_score = 0
        text_arr = text.split()

        for bad_phrase in self.bad_phrases:
            if bad_phrase['phrase'] == text or bad_phrase['phrase'] in text:
                worry_score += bad_phrase['score']
            elif "alt" in bad_phrase:
                for alt in bad_phrase['alt']:
                    if alt == text or alt in text:
                        worry_score += bad_phrase['score']

        for bad_word in self.bad_words:
            if bad_word['word'] in text_arr:
                worry_score += bad_word['score']
            elif "alt" in bad_word.keys() and text_arr in bad_word['alt']:
                worry_score += bad_word['score']

        return worry_score

    @staticmethod
    def clean_text(text: str) -> str:
        return text.replace(",", "").replace(".", "")

    def recognize_text(self, text: str) -> int:
        return self.recognize_phrase(self.clean_text(text))
