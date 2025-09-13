import os
from collections import Counter
from functions.preprocess_data import preprocess_data
from functions.embed_data import embed_data
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction import DictVectorizer
import pickle
import joblib
import numpy as np

def get_word_dict(tokens):
    word2idx = {}
    with open("data/vocab.txt", "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            w, sidx = s.rsplit(":", 1)
            word2idx[w] = int(sidx)
    return word2idx

# Function to load vectors from file
def load_vectors(file_path, sparse=False):
    vectors = []
    # Each line: "#<review_index>,val1,val2,..." or "#<review_index>,idx1:val1,idx2:val2,..."
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # Parse the line into index and vector parts
            parts = line.strip().split(",", 1)
            # Check if we have both index and vector
            if len(parts) < 2:
                continue
            vec_str = parts[1]
            # Handle sparse format (count vectors)
            if sparse:
                vec = {}
                for item in vec_str.split(","):
                    if ":" in item:
                        idx, val = item.split(":")
                        vec[int(idx)] = int(val)
                vectors.append(vec)
            else:
                # Convert string "[0.1, 0.2, ...]" into Python list
                vec_str = vec_str.strip("[]")
                vec = np.array([float(x) for x in vec_str.split(",")])
                vectors.append(vec)
    return vectors



def fused_predict(predict_data, word_dict, models_dir="models"):
    """
    Run predictions using all models in the folder and fuse results.

    Parameters:
        predict_data: input text data
        word_dict: dictionary for embeddings
        models_dir: path to models folder

    Returns:
        dict with individual predictions and fused prediction
    """
    count_vectorizer_path = "vectorizer/count_vectorizer.pkl"
    count_vectorizer = joblib.load(count_vectorizer_path)


    # --- Preprocess ---
    predict_data = preprocess_data(predict_data, data_type="Title")
    word_dict = get_word_dict(predict_data)
    ft_unweighted, ft_weighted = embed_data(predict_data, type="review_title", embed_lang_model="FastText", word_dict=word_dict)  # weighted vectors

    X_count_data = load_vectors("data/review_title_count_vectors.txt", sparse=True)
    X_count_data = count_vectorizer.transform(X_count_data)
    X_weighted_ft_data = StandardScaler().fit_transform(np.vstack(ft_weighted))
    X_unweighted_ft_data = StandardScaler().fit_transform(np.vstack(ft_unweighted))


    # --- Collect models ---
    model_files = [
        f for f in os.listdir(models_dir)
        if f.endswith(".pkl") or f.endswith(".sav")
    ]

    if not model_files:
        raise FileNotFoundError(f"No model files found in {models_dir}")

    predictions = []

    # --- Run predictions for each model ---
    for f in model_files:
        model_path = os.path.join(models_dir, f)
        model = joblib.load(model_path)
        print(f"Loaded model from {model_path}")
        if f.endswith("count.pkl"):
            # This weight 3 times more than others
            model_weight = 3
            pred = model.predict(X_count_data)
            for w in range(model_weight):
                predictions.append(pred[0])  # assuming single-sample prediction
        elif f.endswith("ft_weighted.pkl"):
            model_weight = 1
            pred = model.predict(X_weighted_ft_data)
            for w in range(model_weight):
                predictions.append(pred[0])  # assuming single-sample prediction
        elif f.endswith("ft_unweighted.pkl"):
            model_weight = 1
            pred = model.predict(X_unweighted_ft_data)
            for w in range(model_weight):
                predictions.append(pred[0])  # assuming single-sample prediction
    # --- Fuse results (majority vote) ---
    print("Individual model predictions:", predictions)
    counter = Counter(predictions)
    fused = counter.most_common(1)[0][0]

    return {
        "individual_predictions": predictions,
        "fused_prediction": fused
    }
