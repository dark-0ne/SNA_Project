from pymongo import MongoClient
import csv

client = MongoClient('127.0.0.1:28847',
                     username='SNA_APP',
                     password='n2zkEtKJ2YHpQe9c',
                     authSource='admin')

db = client["dblp"]
collection = db["publications2"]

docs_to_insert = []
with open("parsed.csv", 'r') as file:
    csvreader = csv.reader(file, delimiter=";")
    next(csvreader)
    for row in csvreader:
        doc = {"year":row[1],"title":row[0],"author":row[2].split(":"),"school":row[3].split(":")}
        if doc["school"][0] == "":
            del doc["school"]
        docs_to_insert.append(doc)

        if len(docs_to_insert)==500:
            collection.insert_many(docs_to_insert)
            docs_to_insert.clear()
        
        
    if len(docs_to_insert)>0:
        collection.insert_many(docs_to_insert)
