def getMongoClient(portInput=None):
    from pymongo import MongoClient
    host= 'localhost'
    port = 27017
    if portInput != None:
        port = portInput
    client = MongoClient(host, port) #connect to MongoDB server
    
    return client

def getMongoIntoPandas(portInput, database_name, collection_name, query):
    import pandas as pd
    client = getMongoClient(portInput)
    db = client[database_name]
    collection = db[collection_name]
    if query != None:
        data = pd.DataFrame(list(collection.find(query)))
    else:
        data = pd.DataFrame(list(collection.find()))
    
    return data

def getUsersUnwrittenToMongoDB(collection, listOfIds, MongoDBField, influencerScreenNamesLowerCaseToProper):
    tweetCursor = collection.find({}, no_cursor_timeout=True)
    usersToWrite = set()
    for user in listOfIds:
        usersToWrite.add(str(user).lower())
        
    userAlreadyWritten = set([])
    for userInfo in tweetCursor:
        if str(userInfo[MongoDBField]).lower() in usersToWrite:
            userAlreadyWritten.add(str(userInfo[MongoDBField]).lower())

    usersUnwritten = usersToWrite.difference(userAlreadyWritten)
    
    if len(influencerScreenNamesLowerCaseToProper) != 0:
        usersUnwrittenProper = set()
        for user in usersUnwritten:
            usersUnwrittenProper.add(influencerScreenNamesLowerCaseToProper[user])
        return usersUnwrittenProper
    else:
        return usersUnwritten

def getUsersWrittenToMongoDB(collection, MongoDBField):
    tweetCursor = collection.find({}, {MongoDBField:1}, no_cursor_timeout=True)
    usersWrittenToMongoDB = set([])
    for userInfo in tweetCursor:
        usersWrittenToMongoDB.add(str(userInfo[MongoDBField]))

    return usersWrittenToMongoDB
