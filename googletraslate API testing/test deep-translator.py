from deep_translator import GoogleTranslator, single_detection

translated = GoogleTranslator(source='auto', target='ru').translate(text="text")
print(GoogleTranslator(source='auto', target='ru').translate(text="Hdllo guys"))

lang = single_detection('аuto', '890b0181297b796cda6ca4daec5ecb11')
print(lang)

# do this
# pip install -U deep-translator

# if
# NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl'
# \module is compiled with 'LibreSSL 2.8.3'. See:
# \https://github.com/urllib3/urllib3/issues/3020 warnings.warn(

# pip install urllib3=1.26.15
# if don't work
# pip install --upgrade pip

# or
# brew install openssl@1.1
# pip3 install urllib3==1.26.15

# or just
# pip3 install urllib3==1.26.15

# 890b0181297b796cda6ca4daec5ecb11 -- api-key