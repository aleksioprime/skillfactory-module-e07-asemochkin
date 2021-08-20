from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_caching import Cache
import os

app = Flask(__name__)
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')

mongo_client = MongoClient()
db_mongo = mongo_client.dashboard.collection

cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://{redis_host}:6379/0'.format(redis_host=REDIS_HOST)})

@app.route('/')
def hello():
    return "Hello World!"

# эндпойнт показа перечня всех объявлений
@app.route('/messages', methods=['GET'])
@cache.cached()
def view_messages():
    if request.method == 'GET':
        res = db_mongo.find()
        res_string = str([s for s in res])
        return jsonify({'ok': True, 'messages': res_string}), 200

# эндпойнт для добавления объявления POST-запросом
@app.route('/add_message', methods=['POST'])
@cache.cached()
def add_message():
    data = request.args
    print(data)
    if request.method == 'POST':
        if data.get('text'):
            res = db_mongo.insert_one(dict(data))
            return jsonify({'ok': True, 'message': 'Message created successfully % s ' % res.inserted_id}), 200
        else:
            return jsonify({'ok': False, 'message': 'Text should present'}), 400

# эндпойнт получения существующего объявления по ID GET-запросом
@app.route('/message/<message_id>', methods=['GET'])
@cache.cached()
def message_by_id(message_id):
    if request.method == 'GET':
            res = db_mongo.find_one(ObjectId(message_id))
            return jsonify({'ok': True, 'message': 'Message found  % s ' % res}), 200

# эндпойнт добавления тега к существующему объявлению POST-запросом
@app.route('/tag/<message_id>', methods=['POST'])
@cache.cached()
def add_tag_to_message(message_id):
    data = request.args
    if request.method == 'POST':
        if data.get('text'):
            res = db_mongo.update_one({"_id": ObjectId(message_id)}, {"$addToSet": {"tags": dict(data)}})
            return jsonify({'ok': True, 'message': 'Tag inserted successfully % s ' % res}), 200
        else:
            return jsonify({'ok': False, 'message': 'Text should present'}), 400

# эндпойнт добавления комментария к существующему объявлению POST-запросом
@app.route('/comment/<message_id>', methods=['POST'])
@cache.cached()
def add_com_to_message(message_id):
    data = request.args
    if request.method == 'POST':
        if data.get('text'):
            res = db_mongo.update_one({"_id": ObjectId(message_id)}, {"$addToSet": {"comments": dict(data)}})
            return jsonify({'ok': True, 'message': 'Comment inserted successfully % s ' % res}), 200
        else:
            return jsonify({'ok': False, 'message': 'Text should present'}), 400

# эндпойнт вывода статистики по выбранному объявлению (кол-во тегов и кол-во комментариев)
@app.route('/stats/<message_id>', methods=['GET'])
@cache.cached()
def stats_by_id(message_id):
    if request.method == 'GET':
        res = db_mongo.find_one(ObjectId(message_id))
        tags = 0 
        comments = 0 
        if 'tags' in res.keys():
            tags =  len(res['tags'])
        if 'comments' in res.keys():
            comments = len(res['comments'])
        return jsonify({'ok': True, 'message': 'Message has {tags} tags and {comments} comments'.format(tags=tags, comments=comments)}), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)