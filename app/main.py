import pandas as pd
pd.set_option('display.max_columns', None)
import lightgbm as lgb
import joblib
import boto3
s3 = boto3.client('s3')
import os
import io
from app.model import MLPipeline


running_locally = os.getenv('RUNNING_LOCAL') is not None
if running_locally:
    print("Running locally: ", running_locally)
    from pathlib import Path
    if Path.cwd().name != 'deploy-python-ml':
        raise Exception("Please run this from within the top directory of `deploy-python-ml`")
    if os.getenv('FILENAME') is None:
        print("FILENAME was not given, reading from model-dev/data")


def load_model():
    with open("app/model/tfidf_vectorizer.joblib", "rb") as filename:
        tfidf_vectorizer = joblib.load(filename)

    with open("app/model/lightgbm-classifier.joblib", "rb") as filename:
        classifier = joblib.load(filename)

    model = MLPipeline(classifier, tfidf_vectorizer)
    return model


def load_s3_data(filename, bucket=None):
    if running_locally:
        print("-- Loading local data --")
        return pd.read_csv(filename)
    else:
        print("-- Loading s3 data --")
        # load test data
        key = filename
        print("Requesting object from Bucket: {} and Key: {}".format(bucket, key))
        obj = s3.get_object(Bucket=bucket, Key=key)
        print("Got object from S3")
        data = io.StringIO(obj['Body'].read().decode('utf-8')) 
        return pd.read_csv(data)


def save_s3_results(df, bucket=None, key='predictions.csv'):
    if running_locally:
        print("-- saving local results --")
        os.makedirs('tmp', exist_ok=True)
        local_filename = f'tmp/{key}'
        print('Local file: ', local_filename)
        df.to_csv(local_filename, index=False)
    else:
        s3_client = boto3.client('s3')
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        s3_client.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())
        print(f'file written to {bucket} --{key}')
    return True


def handler(event, context):
    print("-- Running ML --")
    if running_locally:
        bucket=None
        key = os.getenv('FILENAME', 'model-dev/data/emotion-labels-test.csv')
    else:
        # s3 bucket
        bucket = event['Records'][0]['s3']['bucket']['name']    
        # key = filename = s3 path
        key = event['Records'][0]['s3']['object']['key']
        
    # load the data
    df = load_s3_data(filename=key, bucket=bucket)
    print(df.head())

    model = load_model()
    preds = model.predict(df['text'])
    df['pred'] = preds
    print('-- Predictions --')
    print(df.head())

    save_s3_results(df, bucket=bucket)

    return "Success :)"


if __name__ == "__main__":
    print("NLP ML App")
    if running_locally:
        handler(None, None)


