import tweepy
def getFriendsIDs(api, strID, collectionToWrite):
    import time

    ids = []
    if len(strID) > 0:
        retryCount = 0
        notFinished = True
        while retryCount < 1 and notFinished == True:
            try:
                if retryCount < 1 and notFinished == True:
                    for page in tweepy.Cursor(api.friends_ids, user_id=strID).pages():
                        idsSet = set(ids)
                        for id in page:
                            if not str(id) in idsSet:
                                ids.append(str(id))
                    notFinished = False
                else:
                    print("Error retry count exceeded threshold")
                    import sys
                    sys.exit(0)
            except tweepy.TweepError as e:
                # Just exit if any error
                retryCount += 1
                print("some error : " + str(e))
                print(e)
                if "Failed to send request:" in str(e):
                    print("Check the internet connectivity...")
                    import time
                    print("sleeping for 1 minutes")
                    time.sleep(60)
                    retryCount -= 1

    if len(ids) > 0:
        friendIDsStr = []
        for potentialOrdinaryUser in ids:
            try:
                friendIDsStr.append(str(potentialOrdinaryUser))
            except Exception as e: 
                print(e)
        
        if len(friendIDsStr) > 0:
            infoToWrite = []
            d = {}
            d["_id"] = strID
            d["friends"] = friendIDsStr
            infoToWrite.append(d)
        
            try:
                from datetime import datetime
                collectionToWrite.insert_many(infoToWrite, ordered=False)
                infoToWrite = []
                print("SUCCESS written " + str(len(ids)) + " friends to MongoDB for " + strID + " " + str(datetime.now()))
            except Exception as e: 
                print(e)
                import sys
                sys.exit()

def mainProcessFriends(api, db_name, collectionName, ids, portInput):
    from datetime import datetime
    print("Starting Collecting Friends")
     
    from MongoDBInterface import getMongoClient
    client = getMongoClient(portInput)
    db = client[db_name]
    collectionToWrite = db[collectionName]

    from MongoDBInterface import getUsersUnwrittenToMongoDB
    usersUnwritten = getUsersUnwrittenToMongoDB(collectionToWrite, ids, "_id", {})
    print("Users unwritten " + str(len(usersUnwritten)))
    
    for strID in usersUnwritten:
        getFriendsIDs(api, strID, collectionToWrite)
    
    print("Finished Collecting Friends " + str(datetime.now()))