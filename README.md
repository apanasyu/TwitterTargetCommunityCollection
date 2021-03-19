# TwitterTargetCommunityCollection
Part of PhD research at Syracuse University. The code is related to quickly identifying users that are from a city of interest and the influencers for the city on Twitter. For example, Twitter users that are from Syracuse NY and the corresponding influencers are the city mayor, local news, local sports, etc. This is done leveraging Google search and network follower-followee structure with minimal human in the loop verification.

# High Level Approach
Given a city of interest and a list of other cities from which to distinguish from:
(1) use Google search to discover known city-level geo-influencers
(2) followers of influencers from step 1 are used to establish a city community
(3) collect new geo-influencers (potential) that are followed by city community from step 2
(4) a modified TF-IDF measure is used to rank new geo-influencers from step 3. 
(geo-influencer = influencer whose followers are concentrated in a geographic area)

![image](https://user-images.githubusercontent.com/80060152/111801025-eb60c800-88a2-11eb-9756-86dd51585db3.png)

# Preliminaries:

Utilizing Ubuntu operating system, MongoDB for storing Tweets, Python 3.x as the programming language.

Python interfaces with MongoDB using pymongo (pip install pymongo), with Twitter using tweepy (pip install tweepy). Other library dependencies: pip3 install google (https://pypi.org/project/google/#files)

Important: Before using the Twitter API you are required to create and register your app (this is free), see:

https://developer.twitter.com/en/docs/twitter-api/getting-started/guide

(By registering an app you will obtain four tokens: consumer key, consumer secret, access token, and access secret. Go inside TwitterAPI.py and put these keys inside getAPI method).

# Influential users and communities for Minsk, Belarus vs. Moscow, Russia
Step 1: User needs to specify 2 or more queries that contain locations of interest and keyword 'Twitter'. Twitter screennames from top 100 URLs from Google search are utilized. Twitter API used to collect information about each screenname verifying that it is a user on Twitter and providing additional information such as description, number of followers, and other features from user's profile.

    queries = ["Minsk Belarus Twitter", "Moscow Russia Twitter"]
    import time
    for query in queries:
        potentialInfluencerToWebHit = googleSearch(query)
        print(potentialInfluencerToWebHit)

        collectionName = query.replace(" ", "")
        collectionToWrite = db[collectionName]
        collectionToWrite.drop()
        mainProcessScreenNames(twitterAPI1, db_name, collectionName, potentialInfluencerToWebHit.keys(), portInput, True)

        generateCSVFileWithUserInfo(collectionToWrite, potentialInfluencerToWebHit, outputDir)
        time.sleep(120) #wait 2 minutes before queries to google so that a bot is not suspected


For each query this will generate a CSV file that needs to be examined by hand:
![image](https://user-images.githubusercontent.com/80060152/111816094-cbd19b80-88b2-11eb-8596-3c22ef48db34.png)

Step 2: An initial set of geo-influencers is selected from the CSV files using fields such as the self-reported location and description
For Moscow Russia we choose: moscowgov, KremlinRussia_E
For Minsk Belarus we choose: franakviacorka, BelarusFeed
(it is critical to select influencers that are related to the geographic area of interest, at least 2 influencers are selected and interesection of their followers is used to form community. If not enough followers are found to intersect it is recommended that more influencers are loaded).



