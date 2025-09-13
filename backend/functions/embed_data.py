import os
import re
import pandas as pd
from collections import Counter
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import ast
from gensim.models import FastText
import joblib

def get_tfidf_weighted_embeddings(tfidf_features, feature_names, embedding_dim, lang_model_dict):
    n_docs = tfidf_features.shape[0]
    doc_vectors = np.zeros((n_docs, embedding_dim))

    for i in range(n_docs):
        row = tfidf_features[i]
        weighted_sum = np.zeros(embedding_dim, dtype=np.float32)
        for idx, weight in zip(row.indices, row.data):
            word = feature_names[idx]
            if word in lang_model_dict:
                vec = lang_model_dict[word]
                weighted_sum += vec * weight

        doc_vectors[i] = weighted_sum

    return doc_vectors


def get_review_vector(tokens, lang_model):
    if isinstance(tokens, str):
        words = ast.literal_eval(tokens)
    else:
        words = tokens
    # keep only words in model's vocab
    word_vecs = [lang_model.wv[word] for word in words if word in lang_model.wv]
    return np.sum(word_vecs, axis=0) if word_vecs else np.zeros(lang_model.vector_size)


def embed_data(tokens, type='title', embed_lang_model='FastText', word_dict={}):
    out_path = f"data/{type}_count_vectors.txt"

    # Step 1: Save count vector
    with open(out_path, "w", encoding="utf-8") as fout:
        for review_index, ts in enumerate(tokens.values):
            ctr = Counter()
            for t in ts:
                idx = word_dict.get(t)
                if idx is not None:
                    ctr[idx] += 1

            # Format: "#<review_index>,idx:count,idx:count,..."
            
            parts = [f"{i}:{ctr[i]}" for i in sorted(ctr)]
            fout.write(f"#{review_index},{','.join(parts)}\n")
    
    # Step 1: Redefine and Train FastText model (Use a smaller vector size for Title, as its vocab is large)
    ft_model = FastText(
        vector_size=500,
        min_n=2,      # smallest ngram
        max_n=6,      # largest ngram
        sg=1          # 1=skipgram, 0=CBOW
    ) 

    w2v_model = Word2Vec(
        vector_size=500,
        window=5,
        min_count=2,
        workers=os.cpu_count(),
        sg=1          # 1=skipgram, 0=CBOW
    )

    ft_model.build_vocab(corpus_file=f"data/{type}_corpus.txt")
    ft_model.train(f"data/{type}_corpus.txt", epochs=ft_model.epochs, total_examples=ft_model.corpus_count, total_words=ft_model.corpus_total_words)

    # Step 2: Processed through the tokens and calculate unweighted vector
    processed_review = tokens.apply(lambda tokens_str: " ".join(tokens_str))
    unweighted_ft_vector = tokens.apply(get_review_vector, lang_model=ft_model)
    # Step 3: Apply TF-IDF weighted
    joined_reviews = processed_review.values.tolist()
    t_vectorizer_path = "vectorizer/tfidf_vectorizer.pkl"
    tVectorizer = joblib.load(t_vectorizer_path)
    tfidf_features = tVectorizer.fit_transform(joined_reviews) # generate the tfidf vector representation for all articles
    doc_ft_vectors = get_tfidf_weighted_embeddings(tfidf_features, tVectorizer.get_feature_names_out(), embedding_dim=ft_model.vector_size, lang_model_dict=ft_model.wv)
    ft_weighted_vectors = [vec.tolist() for vec in doc_ft_vectors]

    return unweighted_ft_vector, ft_weighted_vectors
