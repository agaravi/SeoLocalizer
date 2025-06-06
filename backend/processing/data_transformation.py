import re

def clean_text(text):
    # Elimina caracteres no traducibles 
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticonos
        u"\U0001F300-\U0001F5FF"  # símbolos 
        u"\U0001F680-\U0001F6FF"  # transporte y mapas
        u"\U0001F1E0-\U0001F1FF"  # banderas
        u"\U00002700-\U000027BF"  # símbolos varios
        u"\U000024C2-\U0001F251"  # otros símbolos
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

