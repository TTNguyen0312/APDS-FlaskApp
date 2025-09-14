from nltk.tokenize import RegexpTokenizer
import pandas as pd


def tokenize_df(data):
    tokenizer = RegexpTokenizer(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)?")
    return data.apply(lambda text: [token.lower() for token in tokenizer.tokenize(text) if len(token) > 1])

