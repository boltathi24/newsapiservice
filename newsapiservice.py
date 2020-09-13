from bson import json_util
from flask import Flask,jsonify,request
import requests
from pymongo import MongoClient
import json
app = Flask(__name__)
from bson.json_util import dumps
from bson.json_util import loads


class GetNews:

    @classmethod
    def getNews(cls,query):

        resp = requests.get("http://newsapi.org/v2/everything?q="+query+"&sortBy=publishedAt&apiKey=19d7070e247441b6910afb5922cc1313")

        response=None
        if resp.status_code != 200:
            response=json.loads( {"message": "Unsucessful"})
        else:
            response= resp.json()

        return response


class PyMongoDB():
    def __init__(cls):
        cls.con = None
        cls.db = None

    @classmethod
    def setDBConnection(cls):
        cls.con = MongoClient('35.185.53.42', 27017)
        cls.db=cls.con.myDB

    @classmethod
    def getData(cls,query):
        cursor = cls.db.news.find({"category":query},{'_id': False})
        js = loads(dumps(cursor))
        print(js)
        return {"message":js}

    @classmethod
    def insertData(cls,json,category):
        cls.db.news.insert({"news":json,"category":category})

    @classmethod
    def updateData(cls,json,category):
        resp=cls.db.news.update({"category":category},{"$set":{"news":json}},upsert = True)

@app.route('/updateNews',methods=['GET'])
def refreshNews():
    response=None
    try:
        category=request.args.get('category').lower()
        jsonv=GetNews.getNews(category)
        print(jsonv)
        PyMongoDB.updateData(jsonv,category)
        return jsonify(({"message":"success"}))
    except Exception as e:
        return jsonify(({"message":"Exception"}))


# @app.route('/sample',methods=['GET'])
# def sample():
#     return PyMongoDB.insertData()

@app.route('/getnewsfromdb',methods=['GET'])
def getData():
    return PyMongoDB.getData(request.args.get('category'))

@app.route('/getnews',methods=['GET'])
def getNewsFromApi():
    return GetNews.getNews(request.args.get('category'))

@app.route('/getNewsCategories',methods=['GET'])
def getNewsCategories():
    news=['Business','entertainment','General','Health','Science','Sports','Technology']
    return jsonify({"categories":news})

if __name__ == "__main__":
    PyMongoDB.setDBConnection()
    app.run(port=5000,debug=True)
