from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from aitextgen import aitextgen
import botocore
import boto3
import os
from os.path import exists


access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret = os.getenv('AWS_SECRET_ACCESS_KEY')

s3 = boto3.resource(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret
)

BUCKET_NAME = 'lyrics-app'
KEY = 'ATG_20211117_134132/pytorch_model.bin'
file_path = f'models/{KEY}'


file_exists = exists(file_path)

if not file_exists:
    s3.Bucket(BUCKET_NAME).download_file(KEY, file_path)

app = Flask(__name__)
api = Api(app)
CORS(app)

folder = 'models/ATG_20211117_134132/'
ai = aitextgen(model_folder=folder, to_gpu=False)


class status (Resource):
    def get(self):
        try:
            return {'data': 'Api is Running'}
        except Exception as error:
            return {'data': str(error)}


def generate(prompt=None):
    if prompt is None:
        prompt = ''
    return ai.generate_one(prompt=prompt,
                           temperature=0.8,
                           max_length=500).replace('. ', '\n')


class Lyric(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("prompt")
        args = parser.parse_args()
        prompt = args['prompt']
        return jsonify({'lyrics': generate(prompt)})


api.add_resource(status, '/')
api.add_resource(Lyric, '/lyrics/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)