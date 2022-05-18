import json
import struct
import time
from urllib import parse, request
from urllib.error import HTTPError, URLError

import numpy as np
import pyaudio
import speech_recognition


class Listener(object):
    def __init__(self, api_key: str):
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024 * 4
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True,
                                      frames_per_buffer=self.chunk, output=True)
        self.stop_threshold = 300
        self.google_audio_recognizer_api_key = api_key

    def terminate(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def recognize_audio(self, audio: bytes, lang: str = 'pt-BR') -> str:
        audio_source = speech_recognition.AudioData(audio, self.rate, pyaudio.get_sample_size(self.format))

        flac_data = audio_source.get_flac_data(
            convert_rate=None if audio_source.sample_rate >= 8000 else 8000,
            convert_width=2
        )

        url = "http://www.google.com/speech-api/v2/recognize?{}".format(parse.urlencode({
            "client": "chromium",
            "lang": lang,
            "key": self.google_audio_recognizer_api_key,
        }))

        result = request.Request(url, data=flac_data,
                                 headers={"Content-Type": f"audio/x-flac; rate={audio_source.sample_rate}"})

        try:
            response = request.urlopen(result, timeout=None)
        except HTTPError as e:
            raise speech_recognition.RequestError("recognition request failed: {}".format(e.reason))
        except URLError as e:
            raise speech_recognition.RequestError("recognition connection failed: {}".format(e.reason))
        response_text = response.read().decode("utf-8")

        for line in response_text.split("\n"):
            if not line:
                continue
            result = json.loads(line)["result"]

        if len(result) != 0:
            return result[0]['alternative'][0]['transcript']

        return ''

    def listen(self, talking: bool = False) -> any:
        frames = b""
        time_lapsed = time.time()
        can_exit = False

        while True:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            frames += data

            data_int = struct.unpack(str(self.chunk) + 'h', data)
            ms = sum([number ** 2 for number in data_int]) / len(data_int)
            rms = np.sqrt(ms)

            if talking:
                if rms < self.stop_threshold and not can_exit:
                    time_lapsed = time.time()
                    can_exit = True
                elif rms > self.stop_threshold:
                    can_exit = False

                if seconds_passed(time_lapsed, 1) is True and can_exit:
                    break

            elif rms > self.stop_threshold:
                time_lapsed = time.time()
                can_exit = True

            else:
                if seconds_passed(time_lapsed, 0.5) is True and can_exit:
                    break
                elif seconds_passed(time_lapsed, 2) is True and not can_exit:
                    break

        return frames


def seconds_passed(last_time: float, seconds: float):
    return time.time() - last_time >= seconds
