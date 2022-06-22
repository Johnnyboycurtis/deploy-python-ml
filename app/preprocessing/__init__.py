from .nlp_preprocessing import spacy_tokenizer_lemmatizer, decode_emojis


def clean_text(series):
    processed_text = series.apply(decode_emojis)
    processed_text = processed_text.apply(spacy_tokenizer_lemmatizer)
    #print(processed_text.head())
    return processed_text