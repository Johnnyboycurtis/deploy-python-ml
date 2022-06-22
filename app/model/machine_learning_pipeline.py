from app.preprocessing import clean_text

class MLPipeline:

    def __init__(self, classifier, tfidf_vectorizer):
        self.classifier = classifier
        self.tfidf_vectorizer = tfidf_vectorizer

    def predict(self, series, probability=False):
        processed_text = self.__preprocess(series)
        X = self.tfidf_vectorizer.transform(processed_text)
        if probability:
            preds = self.classifier.predict_proba(X)
        else:
            preds = self.classifier.predict(X)
        return preds

    def __preprocess(self, series):
        return clean_text(series)
