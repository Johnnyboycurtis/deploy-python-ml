
import numpy as np
import pandas as pd
# scikit-learn 
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
import lightgbm as lgb
import joblib

from pathlib import Path
cwd = Path.cwd().name
print("CWD: ", Path.cwd())
if cwd != 'deploy-python-ml':
    print("Run this script from the project home directory (e.g. ~/home/whatever/deploy-python-ml)")
    print("On the terminal, `python build_model.py`")


from app.preprocessing import clean_text

def __build_start_message():
    print("--Building the ML example model--")
    import time
    for i in range(3):
        print(i+1, '...')
        time.sleep(0.5)
    print("go!")


def load_data():
    print("Loading datasets")
    train_df = pd.read_csv("model-dev/data/emotion-labels-train.csv")
    val_df = pd.read_csv("model-dev/data/emotion-labels-val.csv")
    test_df = pd.read_csv("model-dev/data/emotion-labels-test.csv")
    return train_df, val_df, test_df


def build():
    __build_start_message()

    # load data (ignore test)
    train_df, val_df, _ = load_data()

    # Process the text
    print("Preprocessing the raw text")
    # training
    train_df['processed_text'] = clean_text(train_df['text'])
    train_text = train_df['processed_text']
    #y_train = pd.get_dummies(train_df['label'])
    y_train = train_df['label']
    # validation
    val_df['processed_text'] = clean_text(val_df['text'])
    val_text = val_df['processed_text']
    #y_val = pd.get_dummies(val_df['label'])
    y_val = val_df['label']


    # Create the tfidf weights
    print("Creating TFIDF Vectorizer")
    tfidf_vectorizer = TfidfVectorizer(
        min_df=30,
        max_df=0.75,
        max_features=1000,
        ngram_range=(1, 2),
        preprocessor=' '.join,
        sublinear_tf=False
    )

    X_train = tfidf_vectorizer.fit(train_text)

    X_train = tfidf_vectorizer.transform(train_text)

    # save the vectorizer
    with open("app/model/tfidf_vectorizer.joblib", "wb+") as filename:
        joblib.dump(tfidf_vectorizer, filename)



    # Build lightgbm classifier
    print("-- Training... -- ")
    model = lgb.LGBMClassifier(n_estimators=120, objective='multiclass', learning_rate=0.1, num_leaves= 40, colsample_bytree = 0.8,
        subsample = 0.6, reg_alpha = 0.1, reg_lambda = 0.2)
    model.fit(X_train, y_train)
    
    with open("app/model/lightgbm-classifier.joblib", "wb+") as filename:
        joblib.dump(model, filename)

    # Validate the model
    X_val = tfidf_vectorizer.transform(val_text)
    y_pred = model.predict(X_val)
    #print(y_pred)
    print('-- Predictions --')
    val_df['pred'] = y_pred
    print(val_df)
    
    report_str = classification_report(val_df['label'], y_pred)
    print("-- Classification Report --")
    print(report_str)

    return "Success :)"


if __name__ == "__main__":
    build()

