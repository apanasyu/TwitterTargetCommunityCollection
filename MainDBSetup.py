def setupDBUsingSingleUser(twitterAPI1, screenName, maxFollowersToCollectInput, followersDir, portInput, reprocess=False, writeFollowerOnly=False):
    from os import path
    outputDirFollower = 'CollectFollowers/'
    if followersDir != None:
        outputDirFollower = followersDir
    import os
    if not os.path.isdir(outputDirFollower):
        os.mkdir(outputDirFollower)
    
    from MongoDBInterface import getMongoClient
    client = getMongoClient(portInput)
    dbnames = client.list_database_names()
    collectionNeedBePerformed = True
    if screenName in dbnames:
        db = client[screenName]
        if "influencerOverWhichFollowerInfoCollected" in db.list_collection_names():
            collectionNeedBePerformed = False
            
    if collectionNeedBePerformed:
        print("working on " + screenName)
        db_name = screenName
        screenNamesToQuery = [screenName]
        collectionName1 = "influencerInfo"
        collectionName2 = "influencerFollowerSample"
        collectionName3 = "followerInfo"
        collectionName3b = "influencerOverWhichFollowerInfoCollected"
    
        '''step1: collect influencer info'''
        from CollectUserInfo import mainProcessScreenNames
        db = client[db_name]
        mainProcessScreenNames(twitterAPI1, db_name, collectionName1, screenNamesToQuery, portInput)
        
        '''step2: collect a sample of followers for each influencer'''
        db = client[db_name]
        collectionToRead = db[collectionName1]
    
        from MongoDBInterface import getUsersWrittenToMongoDB
        influencerScreenNames = list(getUsersWrittenToMongoDB(collectionToRead, "screenName"))
        if len(influencerScreenNames) > 0:
            '''the screennames from Twitter may have a bit different capitalization, use the format as displayed by Twitter'''
            '''vs. original screenNames used in query'''
            influencerScreenNamesLowerCaseToProper = {}
            for influencerScreenName in influencerScreenNames:
                influencerScreenNamesLowerCaseToProper[influencerScreenName.lower()] = influencerScreenName
            screenNamesToQueryProper = []
            for screenName in screenNamesToQuery:
                if screenName.lower() in influencerScreenNamesLowerCaseToProper:
                    screenNamesToQueryProper.append(influencerScreenNamesLowerCaseToProper[screenName.lower()])
            print("working with ", len(screenNamesToQueryProper), " out of ", len(screenNamesToQuery), " original screenNames")
            
            import os
            if not os.path.isdir(outputDirFollower):
                os.mkdir(outputDirFollower)
            from CollectFollowers import mainProcessFollowers
            if (not os.path.isfile(outputDirFollower+str(screenName.lower())+".pickle")) or reprocess:
                mainProcessFollowers(twitterAPI1, db_name, collectionName2, screenNamesToQueryProper, influencerScreenNamesLowerCaseToProper, portInput, maxFollowersToCollect=maxFollowersToCollectInput, filePathToStoreToInput=outputDirFollower+str(screenName.lower())+".pickle")
            
            if not writeFollowerOnly:
                '''step3: collect profile metadata on each follower'''
                from CollectUserInfo import mainProcessIDs
                userInfoPath = outputDirFollower+str(screenName.lower())+".pickle"
                import pickle
                with open(userInfoPath, "rb") as fp:
                    followers = pickle.load(fp)
                    followersSTR = []
                    for follower in followers:
                        try:
                            followersSTR.append(str(follower))
                        except:
                            print("Error loading follower")

                    followers = followersSTR
                    print(str(len(followers)) + " followers loaded")
                    mainProcessIDs(twitterAPI1, db_name, collectionName3, followers, collectionName3b, portInput)    