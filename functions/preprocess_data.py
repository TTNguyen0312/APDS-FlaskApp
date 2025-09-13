import re
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from spellchecker import SpellChecker
from nltk.stem import WordNetLemmatizer

def clean_tokens(tokens):
    if not isinstance(tokens, list):
        return []
    return [str(t).lower() for t in tokens if t is not None]

def correct_tokens(tokens):
        corrected = []
        spell = SpellChecker()
        for word in tokens:
            if word in spell.unknown([word]):
                suggestion = spell.correction(word)
                corrected.append(suggestion if suggestion else word)
            else:
                corrected.append(word)
        return corrected
    
def remove_stopwords(tokens, stopset):
    return [t for t in tokens if t not in stopset]

def clean_vocab_token(token):
    token = token.lower().strip()
    if re.fullmatch(r"[a-z0-9]+", token) and len(token) > 2:
        return token
    return None


def preprocess_data(tokens: pd.Series, data_type="Title"):
    # --- Step 1: Clean tokens ---
    tokens = tokens.apply(clean_tokens)
    print(tokens)

    # --- Step 2: Spell correction (optional, heavy) ---
    tokens = tokens.apply(correct_tokens)

    # --- Step 3: Remove stopwords ---
    stop_path = Path("data/stopwords_en.txt")
    with open(stop_path, "r", encoding="utf-8") as f:
        stop_words = {line.strip() for line in f if line.strip()}

    tokens = tokens.apply(remove_stopwords, stopset=stop_words)

    # --- Step 4: Lemmatization ---
    lemmatizer = WordNetLemmatizer()
    tokens = tokens.apply(lambda toks: [lemmatizer.lemmatize(w) for w in toks])

    # --- Step 5: Final cleanup ---
    tokens = tokens.apply(
        lambda toks: [clean_vocab_token(t) for t in toks if clean_vocab_token(t)]
    )

    return tokens
