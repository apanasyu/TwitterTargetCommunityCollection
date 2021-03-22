import tweepy
def getFollowerIDs(api, screenName, maxFollowersToCollect, collectionToWrite, filePathToStoreToInput=None):
    print(screenName + " max followers to collect " + str(maxFollowersToCollect))
    filePathToStoreTo = "FollowersTemp.pickle"
    if filePathToStoreToInput != None:
        filePathToStoreTo = filePathToStoreToInput
    import time
    start_time = time.time()

    ids = []
    if len(screenName) > 0:
        print('Working with ' + str(screenName))
        retryCount = 0
        notFinished = True
        while retryCount < 1 and notFinished == True:
            try:
                if retryCount < 1 and notFinished == True:
                    for page in tweepy.Cursor(api.followers_ids, screen_name=screenName).pages():
                        idsSet = set(ids)
                        for id in page:
                            if not str(id) in idsSet:
                                ids.append(str(id))
                        elapsed_time = time.time() - start_time
                        elapsed_minutes = float(elapsed_time)/(60)
                        if elapsed_minutes > 30:
                            start_time = time.time()
                            if len(ids) > 0:
                                import pickle
                                with open(filePathToStoreTo, "wb") as fp:
                                    pickle.dump(ids, fp)
                                    print("written " + str(len(ids)) + " to " + filePathToStoreTo)
                        if len(ids) > maxFollowersToCollect:
                            print("Stopping collection since " + str(maxFollowersToCollect) + " max followers has been reached.")
                            break
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
    
    if filePathToStoreToInput == None:
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
                d["_id"] = screenName
                d["followers"] = friendIDsStr
                infoToWrite.append(d)
            
                try:
                    from datetime import datetime
                    collectionToWrite.insert_many(infoToWrite, ordered=False)
                    infoToWrite = []
                    print("SUCCESS written " + str(len(ids)) + " followers to MongoDB for " + screenName + " " + str(datetime.now()))
                except Exception as e: 
                    print(e)
                    
                    import pickle
                    with open(filePathToStoreTo, "wb") as fp:
                        pickle.dump(ids, fp)
                        print("written " + str(len(ids)) + " to " + filePathToStoreTo)
                    
                    from datetime import datetime
                    print("ERROR process getFollowerIDs from CollectFollowers.py failed to write to MongoDB " + str(datetime.now()))
                    print("written followers to " + filePathToStoreTo)
                    print("for future processing. Exiting...")
                    import sys
                    sys.exit()
    else:
        import pickle
        with open(filePathToStoreTo, "wb") as fp:
            pickle.dump(ids, fp)
            print("written " + str(len(ids)) + " to " + filePathToStoreTo)
            
def mainProcessFollowers(api, db_name, collectionName, screenNames, influencerScreenNamesLowerCaseToProper, portInput, maxFollowersToCollect=1000, filePathToStoreToInput=None):
    from datetime import datetime
    print("Starting Collecting Followers with Follower Sample size = " + str(maxFollowersToCollect) + " " + str(datetime.now()))
     
    from MongoDBInterface import getMongoClient
    client = getMongoClient(portInput)
    db = client[db_name]
    collectionToWrite = db[collectionName]

    from MongoDBInterface import getUsersUnwrittenToMongoDB
    usersUnwritten = getUsersUnwrittenToMongoDB(collectionToWrite, screenNames, "_id", influencerScreenNamesLowerCaseToProper)
    print("Users unwritten " + str(len(usersUnwritten)))
    
    for screenName in usersUnwritten:
        if filePathToStoreToInput != None:
            getFollowerIDs(api, screenName, maxFollowersToCollect, collectionToWrite, filePathToStoreToInput)
        else:
            getFollowerIDs(api, screenName, maxFollowersToCollect, collectionToWrite)
    
    print("Finished Collecting Followers " + str(datetime.now()))