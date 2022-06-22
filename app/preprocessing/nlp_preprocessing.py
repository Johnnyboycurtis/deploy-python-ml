import re
import spacy
nlp = spacy.load("en_core_web_lg")
import emoji
emoji.demojize



def spacy_tokenizer_lemmatizer(text):
    doc = nlp(text)
    lemma_list = []
    for token in doc:
        if token.is_stop is False:
            lemma_list.append(token.lemma_)
    return(lemma_list)




def decode_emojis(text):
    text = emoji.demojize(text).lower()
    text = re.sub('[\W]+', ' ', text.lower())
    return text


