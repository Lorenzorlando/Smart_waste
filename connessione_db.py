from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

uri = "mongodb+srv://lorenzorl:ny1CNZ87907kAaCq@cluster0.jumtxyx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"




client = MongoClient(uri, server_api=ServerApi('1'))
db = client["progetto"] # progetto è il db in mongodb
tab_predizioni = db["predizioni"] 
utenti=db["utenti"] # dove vengono memorizzati gli utenti che si registrano


try:
    client.admin.command('ping')
    print("Connessione riuscita")
except Exception as e:
    print(e)