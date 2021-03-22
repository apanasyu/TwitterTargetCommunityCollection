def googleSearch(query):
    from googlesearch import search
    startOffSet = len("https://twitter.com/")
    endOffSet = len("?lang=en")
    potentialInfluencerToWebHit = {}
    count = 0
    for url in search(query, tld="com", num=100, lang="en"):
        print(url)
        if url.startswith("https://twitter.com/") and url.endswith("?lang=en") and not "/status/" in url:
            userName = url[startOffSet:len(url)-endOffSet]
            if not "hashtag/" in userName:
                potentialInfluencerToWebHit[userName.lower()] = count
        count += 1
    
    return potentialInfluencerToWebHit

def generateCSVFileWithUserInfo(collection, potentialUserToHitNumber, outputDir):
    tweetCursor = collection.find({}, no_cursor_timeout=True)
    
    fieldsOfInterest = ['screenName', 'followers_count', 'location', 'name', 'created_at', 'description']
    rows = [['WebHitNumber']+fieldsOfInterest]
    for userInfo in tweetCursor:
        row = [potentialUserToHitNumber[userInfo['screenName'].lower()]]
        for field in fieldsOfInterest:
            row.append(userInfo[field])
        print(row)
        rows.append(row)

    writeRowsToCSV(rows, outputDir+collection.name+".csv")

def formCommunities(screenNames, outputDir, minFriend, maxFriend, maxFollower, portInput):
    screenNameToFollowers = {}
    for screenName in screenNames:
        userInfoPath = outputDir+str(screenName.lower())+".pickle"
        import pickle
        with open(userInfoPath, "rb") as fp:
            followers = pickle.load(fp)
            followersSTR = set([])
            for follower in followers:
                try:
                    followersSTR.add(str(follower))
                except:
                    print("Error loading follower")

            followers = followersSTR
            screenNameToFollowers[screenName] = followers
    
    #iterate over possible pairs
    followersOfInterest = set([])
    for i in range(0,len(screenNames),1):
        for j in range(0,len(screenNames),1):
            if i < j:
                mutualFollowers = screenNameToFollowers[screenNames[i]].intersection(screenNameToFollowers[screenNames[j]])    
                followersOfInterest = followersOfInterest.union(mutualFollowers)
    
    print(str(len(followersOfInterest)) + " followers of interest by iterating over every pair of influencers")
    from MongoDBInterface import getMongoClient
    client = getMongoClient(portInput)
    finalCommunity = set([])
    for db_name in screenNames:
        db = client[db_name]
        collection = db["followerInfo"]
        
        tweetCursor = collection.find({}, no_cursor_timeout=True)
        
        fieldsOfInterest = ['followers_count', 'friends_count']
        for userInfo in tweetCursor:
            if str(userInfo['id_str']) in followersOfInterest:
                if (userInfo['followers_count'] <= maxFollower and
                    userInfo['friends_count'] <= maxFriend and
                    userInfo['friends_count'] >= minFriend):
                    finalCommunity.add(str(userInfo['id_str']))
                
    print(str(len(finalCommunity)) + " final community after applying thresholds")
           
    return finalCommunity

def writeRowsToCSV(rows, fileToWriteToCSV):
    import csv
    if len(rows) > 0:
        with open(fileToWriteToCSV, "w") as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(rows)
            fp.close()
            print("Written " + str(len(rows)) + " rows to: " + fileToWriteToCSV)

def loadFriends(collectionToRead):
    usersCommunityFollows = {}
    query = {}
    tweetCursor = collectionToRead.find(query, no_cursor_timeout=True)
    for userInfo in tweetCursor:
        usersThatUserOfCommunityFollows = userInfo["friends"]
        for friend in usersThatUserOfCommunityFollows:
            if not friend in usersCommunityFollows:
                usersCommunityFollows[friend] = 0
            usersCommunityFollows[friend] += 1
    
    return usersCommunityFollows

def getTopNCommunityFollowsInCSV(db_name, collectionName, portInput, usersCommunityFollows, N):
    from operator import itemgetter
    res = sorted(usersCommunityFollows.items(), key = itemgetter(1), reverse = True)[:N] 
    topN = []
    for pair in res:
        topN.append(pair[0])
    print(topN)
    print(res)
    
    from MongoDBInterface import getMongoClient
    client = getMongoClient(portInput)
    db = client[db_name]
    collectionToRead = db[collectionName]

    tweetCursor = collectionToRead.find({}, no_cursor_timeout=True)
    
    fieldsOfInterest = ['screenName', 'followers_count', 'location', 'name', 'created_at', 'description']
    nameToRow = {}
    topNSet = set(topN)
    for userInfo in tweetCursor:
        if str(userInfo["id_str"]) in topNSet:
            row = [usersCommunityFollows[str(userInfo["id_str"])]]
            for field in fieldsOfInterest:
                row.append(userInfo[field])
            nameToRow[str(userInfo["id_str"])] = row

    rows = [['FollowsByCommunity']+fieldsOfInterest]
    for name in topN:
        rows.append(nameToRow[name])
    
    writeRowsToCSV(rows, outputDir+db_name+"TopNMostFrequentlyFollowed.csv")
        
if __name__ == '__main__':
    pass

    outputDir = "programOutput/"
    import os
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
    followersDir = "collectFollowers/"
    import os
    if not os.path.isdir(followersDir):
        os.mkdir(followersDir)

    from TwitterAPI import getAPI
    twitterAPI1 = getAPI()
    port = 27020
    step0 = False
    if step0:
        print("applying google search")
        db_name = "TempInfluencersFromGoogleSearch"
        from MongoDBInterface import getMongoClient
        client = getMongoClient(port)
        from CollectUserInfo import mainProcessScreenNames
        db = client[db_name]
        
        queries1 = ["Minsk Belarus Twitter", "Moscow Russia Twitter", "Moskva Russia Twitter"]
        queries2 = ["Buffalo NY Twitter", "Syracuse NY Twitter"]
        queries = queries1+queries2
        import time
        for query in queries:
            potentialInfluencerToWebHit = googleSearch(query)
            print(potentialInfluencerToWebHit)
            
            collectionName = query.replace(" ", "")
            collectionToWrite = db[collectionName]
            collectionToWrite.drop()
            mainProcessScreenNames(twitterAPI1, db_name, collectionName, potentialInfluencerToWebHit.keys(), port, True)
        
            generateCSVFileWithUserInfo(collectionToWrite, potentialInfluencerToWebHit, outputDir)
            time.sleep(120) #wait 2 minutes before queries to google so that a bot is not suspected
    
    influencer1 = ['moscowgov', 'MID_RF', 'mfa_russia']
    influencer2 = ['franakviacorka', 'BelarusMID', 'BelarusFeed', 'Tsihanouskaya']
    influencer3 = ['SyracuseUNews', 'Syracuse1848', 'AndrewDonovan', 'BenWalsh44', 'SyracusePolice', 'Cuse_Tennis']
    influencer4 = ['WKBW', 'SPECNewsBuffalo', 'NWSBUFFALO', 'BPDAlerts']
    step1 = False #collect followers
    if step1:
        influencers = influencer1+influencer2+influencer3+influencer4 
        '''collect influencer's followers and profile information of each follower'''
        from MainDBSetup import setupDBUsingSingleUser
        maxFollowerToCollect = 500000
        for influencerScreenName in influencers:
            setupDBUsingSingleUser(twitterAPI1, influencerScreenName, maxFollowerToCollect, followersDir, port)

    step2 = False #form communities
    communities = {}
    communities["ComMoscowRussiaTwitter"] = influencer1
    communities["ComMinskBelarusTwitter"] = influencer2
    communities["ComSyracuseNYTwitter"] = influencer3
    communities["ComBuffaloNYTwitter"] = influencer4
    if step2:
        minFriend = 10
        maxFriend = 25
        maxFollower = 500
        
        for communityName in communities:
            print("working on community for: " + str(communityName))
            followersMeetingThreshold = formCommunities(communities[communityName], followersDir, minFriend, maxFriend, maxFollower, port)
            from CollectFriends import mainProcessFriends
            mainProcessFriends(twitterAPI1, communityName, "friendsOfCommunity", followersMeetingThreshold, port)
    
    from TwitterAPI import getAPI2
    twitterAPI1 = getAPI2()              
    step3 = False
    if step3: #collect info on those users followed by community
        for communityName in communities:
            db_name = communityName
            collectionName = "friendsOfCommunity"
            
            from MongoDBInterface import getMongoClient
            client = getMongoClient(port)
            db = client[db_name]
            collectionNeedBePerformed = True
            if "communityOverWhichFriendInfoCollected" in db.list_collection_names():
                collectionNeedBePerformed = False
            
            if collectionNeedBePerformed:
                collectionToRead = db[collectionName]
                usersCommunityFollows = loadFriends(collectionToRead)
                  
                from CollectUserInfo import mainProcessIDs
                friends = list(usersCommunityFollows.keys())
                print(list(friends))
                print(str(len(friends)) + " friends loaded")
                
                collectionNameToWrite = "friendInfo"
                collectionNameToWrite2 = "communityOverWhichFriendInfoCollected"
                mainProcessIDs(twitterAPI1, db_name, collectionNameToWrite, friends, collectionNameToWrite2, port, True)   
                
    step4 = True
    if step4: #identify top ranked using frequency and TF-IDF
        communityToCommunityFollows = {}
        for communityName in communities:
            db_name = communityName
            collectionName = "friendsOfCommunity"
            
            from MongoDBInterface import getMongoClient
            client = getMongoClient(port)
            db = client[db_name]
            collectionToRead = db[collectionName]
            usersCommunityFollows = loadFriends(collectionToRead)
            communityToCommunityFollows[communityName] = usersCommunityFollows
            topRankedUsingFrequency = 50
            getTopNCommunityFollowsInCSV(db_name, "friendInfo", port, usersCommunityFollows, topRankedUsingFrequency)
        
        from TFIDF import generateTFIDFRanking
        minFollowsByCommunity = 10
        dictionary, influencerToDictCount, tfidf, indexTFIDF, lsi_model, indexLSI, communityLabels, communityVectorsLSI, communityVectorsTFIDF = generateTFIDFRanking(communityToCommunityFollows, minFollowsByCommunity)
        topNInfluencersPerCommunity = 500
        from TFIDF import writeTopNVectors
        writeTopNVectors(communityToCommunityFollows, dictionary, communityVectorsTFIDF, topNInfluencersPerCommunity, port, outputDir)