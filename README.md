# AutoT
Develop an autonomous Twitter account powered by Babyagi and LangChain that dynamically retrieves tweets from specific accounts, analyzes sentiment and engagement patterns, and generates tweets that mirror identified tones and styles. The project aims to autonomously schedule and post tweets optimized for engagement, fostering an engaged following to generate revenue through Twitter ads.

* Babyagi will require persistent storage, local SQLite should be sufficient.

* Pinecone should be used for tweets and sentiment analyses

* Avoid twitter api's, rate limits etc by using selenium if possible





# config.py
PINECONE_API_KEY = 'YOUR PINECONE API KEY'
PINECONE_ENVIRONMENT = 'us-east-1'
PINECONE_INDEX_NAME = 'tweet-analysis'  # Replace with your actual index name
PINECONE_HOST = 'https://yourpineconehost.pinecone.io'

OPENAI_API_KEY = 'YOUR OPENAI API KEY'

TWITTER_URL = 'https://x.com'
CHROMEDRIVER_PATH = 'C:/Development/chromedriver130.exe'

# Without the @ symbol
TARGET_ACCOUNTS = ['elonmusk', 'MarioNawfal']


# Mode configuration: Set to 'test' to output tweets to console or file, 'prod' for actual posting
MODE = 'test'  # Change to 'prod' when ready to post

# Scheduling configurations
COLLECTION_INTERVAL = 1      # in minutes (e.g., collect tweets every hour)
GENERATION_INTERVAL = 3      # in minutes (e.g., generate tweets every 3 hours)
ENGAGEMENT_MONITOR_INTERVAL = 10  # Monitor engagement every 1 minute for testing

# times to post tweets (24-hour format)
POSTING_TIMES = ["09:00", "12:00", "15:00", "18:00"]  