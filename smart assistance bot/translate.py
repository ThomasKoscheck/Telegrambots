# https://github.com/MrS0m30n3/google-translate
import google_translate

def translate(query):
    translator = google_translate.GoogleTranslator()
    result = translator.translate(query.encode('utf-8'), "german")
    return result
        