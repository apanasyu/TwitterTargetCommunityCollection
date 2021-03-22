def generateTFIDFRanking(communityToCommunityFollows, minFreq):
    influencerToFreqGlobal = {}
    for community in communityToCommunityFollows:
        for influencer in communityToCommunityFollows[community]:
            if communityToCommunityFollows[community][influencer] >= minFreq:
                if not influencer in influencerToFreqGlobal:
                    influencerToFreqGlobal[influencer] = communityToCommunityFollows[community][influencer]
                else:
                    influencerToFreqGlobal[influencer] += communityToCommunityFollows[community][influencer]
            
    '''form dictionary'''
    influencers = []
    for influencer in influencerToFreqGlobal:
        if influencerToFreqGlobal[influencer] >= minFreq: 
            influencers.append(influencer)
    
    from gensim import corpora
    dictionary = corpora.Dictionary([influencers])
    influencerToDictCount = {}
    for count in dictionary:
        influencerToDictCount[dictionary[count]] = count
        
    communityLabels = []
    docCountToCommunity = {}
    countryCount = 0
    corpus = []
    for community in communityToCommunityFollows:
        influencerToFreq = communityToCommunityFollows[community]
        locOfInterestCount = []
        for loc in influencerToFreq:
            if loc in influencerToDictCount:
                locOfInterestCount.append(influencerToDictCount[loc])
        
        locOfInterestCountSorted = sorted(locOfInterestCount)
        doc = []
        for count in locOfInterestCountSorted:
            doc.append((count, influencerToFreq[dictionary[count]]))

        corpus.append(doc)
        communityLabels.append(community)
        docCountToCommunity[countryCount] = community
        countryCount += 1
    
    from gensim import models
    tfidf = models.TfidfModel(corpus)

    communityVectorsTFIDF = {}
    corpus_tfidf = tfidf[corpus]
    count = 0
    for doc in corpus_tfidf:
        communityVectorsTFIDF[docCountToCommunity[count]] = doc
        count += 1

    lsi_model = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=500)  # initialize an LSI transformation
    communityVectorsLSI = {}
    corpus_lsi = lsi_model[corpus_tfidf]  # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
    count = 0
    for doc in corpus_lsi:
        communityVectorsLSI[docCountToCommunity[count]] = doc
        count += 1
    
    from gensim import similarities
    indexTFIDF = similarities.MatrixSimilarity(corpus_tfidf)    
    indexLSI = similarities.MatrixSimilarity(corpus_lsi)    
    
    return dictionary, influencerToDictCount, tfidf, indexTFIDF, lsi_model, indexLSI, communityLabels, communityVectorsLSI, communityVectorsTFIDF
    
def writeTopNVectors(communityToCommunityFollows, dictionary, weightedVectors, N, portInput, outputDir):
    for label in weightedVectors:
        weightsTemp = weightedVectors[label]
        communityWeights = {}
        for indexToWeightTuple in weightsTemp:
            communityWeights[indexToWeightTuple[0]] = indexToWeightTuple[1]
            
        topNIndexes, topNToCount = getTopNFromDict(communityWeights, N)
        topNNames = []
        for index in topNIndexes:
            topNNames.append(dictionary[index])
        
        db_name = label
        collectionName = "friendInfo"
        print(label)
        print(topNNames)
        from MongoDBInterface import getMongoClient
        client = getMongoClient(portInput)
        db = client[db_name]
        collectionToRead = db[collectionName]
    
        tweetCursor = collectionToRead.find({}, no_cursor_timeout=True)
        
        fieldsOfInterest = ['screenName', 'followers_count', 'location', 'name', 'created_at', 'description']
        nameToRow = {}
        for userInfo in tweetCursor:
            if str(userInfo["id_str"]) in topNNames:
                row = [communityToCommunityFollows[label][str(userInfo["id_str"])]]
                for field in fieldsOfInterest:
                    row.append(userInfo[field])
                nameToRow[str(userInfo["id_str"])] = row
        
        rows = [['FollowsByCommunity']+fieldsOfInterest]
        for name in topNNames:
            rows.append(nameToRow[name])
        
        from Main import writeRowsToCSV
        writeRowsToCSV(rows, outputDir+label+"TopNusingTFIDF.csv")
            
def getTopNFromDict(dictToSort, N):
    import operator
    sortedDict = sorted(dictToSort.items(), key = operator.itemgetter(1), reverse=True)
    count = 0
    topN = []
    topNToCount = {}
    for result in sortedDict:
        topN.append(result[0])
        topNToCount[result[0]] = float(result[1])
        count += 1
        if count >= N:
            break
    
    return topN, topNToCount
