from datetime import datetime
import tweepy
def extractUserInfo(user, writeDescription=False):
    screenName = str(user['screen_name'])
    created_at = transformTwitterDateStringToProperDateTime(user['created_at'])
    favourites_count = user['favourites_count']
    followers_count = user['followers_count']
    friends_count = user['friends_count']
    geo_enabled = user['geo_enabled']
    id_str = str(user['id_str'])
    listed_count = user['listed_count']
    description = user['description']
    if 'location' in user:
        location = user['location']
    if location == None:
        location = ""
    name = str(user['name'])
    if len(name) > 0:
        numTokensName = len(name.split(' '))
    else:
        numTokensName = 0
    statuses_count = user['statuses_count']
    verified = user['verified']
    
    userInfo = {}
    userInfo["_id"] = id_str
    userInfo["screenName"] = screenName
    userInfo["created_at"] = created_at
    userInfo["favourites_count"] = favourites_count
    userInfo["followers_count"] = followers_count
    userInfo["friends_count"] = friends_count
    userInfo["geo_enabled"] = geo_enabled
    userInfo["id_str"] = id_str
    userInfo["listed_count"] = listed_count
    userInfo["location"] = location
    userInfo["name"] = name
    userInfo["numTokensName"] = numTokensName
    userInfo["statuses_count"] = statuses_count
    userInfo["verified"] = verified
    if writeDescription:
        userInfo["description"] = description
    return userInfo

def transformTwitterDateStringToProperDateTime(twitterDateString):
    return datetime.strptime(twitterDateString,'%a %b %d %H:%M:%S +0000 %Y')

def getFollowerInfoFromListOfScreenNames(api, ids, collectionToWrite, writeDescription=False):
    import os
    import json
    size = 100
    usersToStore = []
    i = 0
    maxRetryCount = 1
    retryCount = 0
    while i < len(ids):
        listOf100Ids = ids[i:i + size]
        notFinished = True
        while retryCount < maxRetryCount and notFinished == True:
            try:
                user_objects = api.lookup_users(screen_names=listOf100Ids, include_entities=True)
    
                for user in user_objects:
                    usersToStore.append(user._json)
                
                if len(usersToStore) > 5000:
                    writeUserInfo(usersToStore, collectionToWrite, writeDescription)
                    usersToStore = []

                i += size
                notFinished = False
            except tweepy.TweepError as e:
                retryCount += 1
                print("some error : " + str(e))
                print(e)
                if "Failed to send request:" in str(e):
                    print("Check the internet connectivity, once connected press any key to continue:")
                    import time
                    print("sleeping for 1 minutes")
                    time.sleep(60)
                    retryCount -= 1
                if retryCount >= maxRetryCount:
                    i += size
                    retryCount = 0
                    notFinished = False
                    print("Error retry count exceeded threshold, skipping batch of users")
        
    if len(usersToStore) > 0:
        writeUserInfo(usersToStore, collectionToWrite, writeDescription)
        usersToStore = []

def writeUserInfo(usersToStore, collectionToWrite, writeDescription=False):
    from datetime import datetime
    import os
    import pickle

    userInfoToStore = []
    for user in usersToStore:              
        userInfo = extractUserInfo(user, writeDescription)
        userInfoToStore.append(userInfo)

    totalWritten = 0
    try:
        collectionToWrite.insert_many(userInfoToStore, ordered=False)
        totalWritten += len(userInfoToStore)
        print("SUCCESS written " + str(totalWritten) + " user info records to MongoDB " + str(datetime.now()))
    except Exception as e: 
        print(e)
        
def mainProcessScreenNames(api, db_name, collectionName, screenNames, portInput, writeDescription=False):
    from datetime import datetime
    print("Starting Collecting User Info " + str(datetime.now()) + " into collection " + collectionName)
     
    from MongoDBInterface import getMongoClient
    if portInput != None:
        client = getMongoClient(portInput)
    else:
        client = getMongoClient()
    db = client[db_name]
    collectionToWrite = db[collectionName]

    from MongoDBInterface import getUsersUnwrittenToMongoDB
    usersUnwritten = list(getUsersUnwrittenToMongoDB(collectionToWrite, screenNames, "screenName", {}))
    print(str(len(usersUnwritten)) + " users unwritten for part 1")
    
    getFollowerInfoFromListOfScreenNames(api, usersUnwritten, collectionToWrite, writeDescription)

    print("Finished Collecting User Info " + str(datetime.now()) + " into collection:" + collectionName)

def mainProcessIDs(api, db_name, collectionName, ids, collectionNameWritesPerformed, portInput, writeDescription=False):
    from datetime import datetime
    print("Starting Collecting User Info " + str(datetime.now()))
                        
    from MongoDBInterface import getMongoClient
    client = getMongoClient(portInput)
    db = client[db_name]
    collectionToWrite = db[collectionName]

    tweetCursor = collectionToWrite.find({}, no_cursor_timeout=True)
    userAlreadyWritten = set([])
    for userInfo in tweetCursor:
        userAlreadyWritten.add(str(userInfo["id_str"]))
    if len(userAlreadyWritten) > 0:
        print(str(len(userAlreadyWritten)) + " userAlreadyWritten")
        count = 0
        for uid in ids[::-1]: #reversed list
            if uid in userAlreadyWritten:
                break
            count += 1
        ids = ids[-count:]
        print(len(ids))
    
    getFollowerInfoFromListOfIDs(api, ids, collectionToWrite, writeDescription)
    
    infoToWrite = []
    d = {}
    d["_id"] = db_name
    infoToWrite.append(d)

    from datetime import datetime
    try:
        db[collectionNameWritesPerformed].insert_many(infoToWrite, ordered=False)
    except:
        print("Error when doing bulk write")

    print("Finished Collecting User Info " + str(datetime.now()))

def getFollowerInfoFromListOfIDs(api, ids, collectionToWrite, writeDescription=False):
    import os
    import json
    size = 100
    usersToStore = []
    i = 0
    maxRetryCount = 1
    retryCount = 0
    while i < len(ids):
        listOf100Ids = ids[i:i + size]
        notFinished = True
        while retryCount < maxRetryCount and notFinished == True:
            try:
                user_objects = api.lookup_users(user_ids=listOf100Ids, include_entities=True)

                for user in user_objects:
                    usersToStore.append(user._json)
                
                if len(usersToStore) > 5000:
                    writeUserInfo(usersToStore, collectionToWrite, writeDescription)
                    usersToStore = []

                notFinished = False
            except tweepy.TweepError as e:
                retryCount += 1
                print("some error : " + str(e))
                print(e)
                if "Failed to send request:" in str(e):
                    print("Check the internet connectivity, once connected press any key to continue:")
                    #userInput = raw_input()
                    import time
                    print("sleeping for 1 minutes")
                    time.sleep(60)
                    retryCount -= 1
                if retryCount > maxRetryCount:
                    i += size
                    retryCount = 0
                    print("Error retry count exceeded threshold, skipping batch of users")
        retryCount = 0
        i += size

    if len(usersToStore) > 0:
        writeUserInfo(usersToStore, collectionToWrite, writeDescription)
        usersToStore = []