from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from aitextgen import aitextgen


app = Flask(__name__)
api = Api(app)
CORS(app)

folder = 'https://lyrics-app-s3.s3.amazonaws.com/models/ATG_20211117_134132/'
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
    app.run()