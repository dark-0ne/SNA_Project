from pymongo import MongoClient
from tqdm import tqdm

client = MongoClient('127.0.0.1:28847',
                     username='SNA_APP',
                     password='n2zkEtKJ2YHpQe9c',
                     authSource='admin')

db = client["dblp"]
collection = db["publications2"]

author_stats = {}

for doc in tqdm(collection.find(),total=6056270):
    cur_authors = doc["author"]

    # Only 1 author
    if len(cur_authors) == 1:
        cur_stats = author_stats.get(cur_authors[0],{"schools":set(),"coauthors":set(),"co_count":0})
        try:
            for school in list(doc["school"]):
                cur_stats["schools"].add(school)
        except KeyError:
            pass
        author_stats[cur_authors[0]] = cur_stats

    # More than 1 author
    else:
        for author in cur_authors:
            cur_stats = author_stats.get(author,{"schools":set(),"coauthors":set(),"co_count":0})

            try:
                for school in list(doc["school"]):
                    cur_stats["schools"].add(school)
            except KeyError:
                pass
            for author2 in cur_authors:
                if author != author2:
                    cur_stats["coauthors"].add(author2)
                    cur_stats["co_count"] += 1

            author_stats[author] = cur_stats

collection = db["authors"]
for key,value in author_stats.items():
    doc = {"author":key,"co_count":value["co_count"],"coauthors":list(value["coauthors"]),"schools":list(value["schools"])}
    collection.insert_one(doc)

