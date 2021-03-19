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
Step 1: User needs to specify 2 or more queries that contain locations of interest and keyword 'Twitter' (alternatively can search for influencers of interest manually and go directly to step 2). Twitter screennames from top 100 URLs from Google search are utilized. Twitter API used to collect information about each screenname verifying that it is a user on Twitter and providing additional information such as description, number of followers, and other features from user's profile.

    queries = ["Minsk Belarus Twitter", "Moskva Russia Twitter"]
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

Step 2: An initial set of geo-influencers is selected from the CSV files using fields such as the self-reported location and description:
For Moscow Russia we choose: moscowgov, MID_RF
For Minsk Belarus we choose: franakviacorka, BelarusMID, BelarusFeed, Tsihanouskaya
(it is critical to select influencers that are related to the geographic area of interest, at least 2 influencers are needed. Intersection of followers for every pair of influencers is selected as this increases the chances that the users are from location of interest. If not enough followers are discovered recommend searching for more influencers).

The followers are collected using (code results in a separate database created for each influencer which contains influencer info and up to 500K of influencer's followers):

    influencer1 = ['moscowgov', 'MID_RF']
    influencer2 = ['franakviacorka', 'BelarusMID', 'BelarusFeed', 'Tsihanouskaya']
    influencers = influencer1+influencer2
    '''collect influencer's followers and profile information of each follower'''
    port = 27020
    from MainDBSetup import setupDBUsingSingleUser
    from TwitterAPI import getAPI
    twitterAPI1 = getAPI()
    maxFollowerToCollect = 500000
    for influencerScreenName in influencers:
        setupDBUsingSingleUser(twitterAPI1, db_name=influencerScreenName, maxFollowerToCollect, followersDir, port)

The communities are formed from followers:

    minFriend = 10
    maxFriend = 50
    maxFollower = 500

    communities = {}
    communities["ComMoscowRussiaTwitter"] = influencer1
    communities["ComMinskBelarusTwitter"] = influencer2
    for communityName in communities:
        print("working on community for: " + str(communityName))
        followersMeetingThreshold = formCommunities(communities[communityName], followersDir, minFriend, maxFriend, maxFollower)
        from CollectFriends import mainProcessFriends
        mainProcessFriends(twitterAPI1, db_name=communityName, collectionName="friendsOfCommunity", followersMeetingThreshold, port)

We want to focus on ordinary followers (by ordinary we mean average users that are not bots and not influencers themselves). In order to increase probability that it is an ordinary follower we focus on those that have: between 10 and 50 friends and less than 500 followers. The developer is free to choose their own thresholds when forming community. A geocoder could also be applied if available as an additional filter, but this should be done with care since most followers will not report a location that is geocodable.

For example for community around Belarus:
14417 followers of interest by iterating over every pair of influencers
823 final community after applying thresholds
Twitter API allows 1 API call per minute when collecting friends of followers. So approximately 823 minutes ~= 14 hours will be required to collect all friends.

The database holding friends will look like this (id string for the user part of the community and the list of ids that he follows):
![image](https://user-images.githubusercontent.com/80060152/111842545-000a8380-88d6-11eb-916f-47824b797d8b.png)

Step 3: The users followed by the community (friends collected in previous step) are filtered and ranked via a TF-IDF model.

The collection process from step 1 and step 2 resulted in a large set of users that are being followed by the community. Below is a depiction of the collection process.

![image](https://user-images.githubusercontent.com/80060152/111843042-d9008180-88d6-11eb-9fa3-1ad7f5ddd72b.png)

For each unique id that is followed by the community we record how many times the id has been followed. We also use Twitter API to look up user profile information for each id. This is accomplished via following code:



The top 10 influencers for 












