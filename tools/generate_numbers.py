import gtts
import time

# produces spanish (latino) audio files for numbers from 0 to 1000

for _i in range(0, 1001):
    print(_i)
    time.sleep(1)
    tts = gtts.gTTS(str(_i), lang="es", tld="com.mx")
    tts.save("../out/%s.mp3" % _i)
