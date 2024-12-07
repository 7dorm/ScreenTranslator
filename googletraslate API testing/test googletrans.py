from googletrans import Translator
translator = Translator(service_urls=[
      'translate.google.com',
    ])

translated = translator.translate('Hdllo guis', dest = 'ru')
print(translated.text)
detected = translator.detect('NSU')
print(detected.lang)