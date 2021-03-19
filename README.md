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

# An example using provided Code
Step 1: User needs to specify 2 or more queries that contain locations of interest. Google search is utilized  
