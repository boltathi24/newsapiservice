from flask import Flask,jsonify,request
import requests
import os
from pymongo import MongoClient
import json
import configparser
from pathlib import Path
app = Flask(__name__)
from bson.json_util import dumps
from bson.json_util import loads


class Configuration:

    @classmethod
    def setFile(cls,file):
        cls.Config = configparser.ConfigParser()
        cls.Config.read(file)


    @classmethod
    def getKeyValue(cls,section,key):
        return cls.Config.get(section,key)



class GetNews:

    @classmethod
    def setApiKey(cls,key,value):
        cls.apiKey=Configuration.getKeyValue(key,value)


    @classmethod
    def getNews(cls,query):

        resp = requests.get("http://newsapi.org/v2/everything?q="+query+"&sortBy=publishedAt&apiKey="+cls.apiKey)

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
        cls.host=None
        cls.port =None

    @classmethod
    def setDBConnection(cls):
        cls.host=Configuration.getKeyValue("mongoDb","hostUrl")
        cls.port=int(Configuration.getKeyValue("mongoDb","port"))
        cls.con = MongoClient(cls.host, cls.port)
        cls.db=cls.con.myDB

    @classmethod
    def getData(cls,query):
        cursor = cls.db.news.find({"subcategory":query},{'_id': False})
        js = loads(dumps(cursor))

        return {"data":js}

    @classmethod
    def getCategories(cls ):
        cursor = cls.db.category.find({}, {'_id': False})
        js = loads(dumps(cursor))

        return {"data": js}

    @classmethod
    def insertData(cls,json,category):
        cls.db.news.insert({"news":json,"category":category})

    @classmethod
    def updateData(cls,jsonvalue,subcategory,category):
        # print({"subcategory":subcategory},{"$set":{"news":"va"}},{"$set":{"category":category}})
        # cursor = cls.db.news.find({}, {'_id': False})
        # js = loads(dumps(cursor))
        # print(js)
        cls.db.news.update({"subcategory":subcategory},{"$set":{"news":jsonvalue,"category":category}},upsert = True)


@app.route('/updateNews',methods=['GET'])
def refreshNews():
    response=None
    try:

        subcategory=request.args.get('subcategory').lower()
        category = request.args.get('category').lower()
        jsonv=GetNews.getNews(subcategory)
        PyMongoDB.updateData(jsonv,subcategory,category)
        return jsonify(({"message":"success"}))
    except Exception as e:
        return jsonify(({"message":"Exception"}))


# @app.route('/sample',methods=['GET'])
# def sample():
#     return PyMongoDB.insertData()

@app.route('/getnews',methods=['GET'])
def getNewsFromDB():
    return PyMongoDB.getData(request.args.get('subcategory'))

@app.route('/fetchnews',methods=['GET'])
def getNewsFromApi():
    return GetNews.getNews(request.args.get('subcategory'))

@app.route('/getallcategories',methods=['GET'])
def getallCategories():
    return PyMongoDB.getCategories()

if __name__ == "__main__":
    Configuration.setFile(Path(__file__).parent / "../config/configuration.ini")
    GetNews.setApiKey("newsApi","apiKey")
    PyMongoDB.setDBConnection()
    app.run(port=5000,debug=True)
