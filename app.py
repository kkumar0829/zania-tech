from flask_restful import Api
from flask import Flask

from handler import UploadPdf, AskQuestion

app = Flask(__name__)
api = Api(app)
app.secret_key = b'x*\xebw\xaet(+\xcaA!UM\xf3w\xf3\x82k\xc8'

# add resources to the API
api.add_resource(UploadPdf, '/v1/upload/')
api.add_resource(AskQuestion, '/v1/ask/')

if __name__ == '__main__':
    app.run(debug=True)
