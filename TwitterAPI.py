import tweepy
import sys

def getAPI(proxyURL=None):
    """
    :mode: either "user" or "app"
    """
    consumer_key = '' # write the key obtained from registering with Twitter API
    consumer_secret = '' # write the key obtained from registering with Twitter API
    access_token = '' # write the key obtained from registering with Twitter API
    access_token_secret = '' # write the key obtained from registering with Twitter API
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True,proxy=proxyURL, retry_count=3, retry_delay=5, retry_errors=set([401, 404, 500, 503]))

    try:
        api.home_timeline()
        return api
    except: 
        #print(str(e))
        print("Could not authenticate API exiting...")
        sys.exit(0)
        
def getLimits():
    print("getAPI")
    twitterAPI = getAPI(apiUserType=True)
    data = twitterAPI.rate_limit_status()
    print(data['resources']['users']['/users/lookup'])
    