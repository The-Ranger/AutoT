import openai
import hashlib
import random
from transformers import pipeline
from pinecone import Pinecone, Index
import config

class TweetAnalyzer:
    def __init__(self):
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        host = config.PINECONE_HOST
        self.index = Index(name=config.PINECONE_INDEX_NAME, host=host, api_key=config.PINECONE_API_KEY)
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        openai.api_key = config.OPENAI_API_KEY
        self.styles = [
            "funny", "sarcastic", "bold and thought-provoking",
            "informative and scientific", "empathetic and inspirational"
        ]

    def get_trending_topics(self):
        trending_topics = ["AI", "space exploration", "end wokeness", "presidential election", "mars", "trump", "kamala"]
        return trending_topics

    def get_random_style(self):
        return random.choice(self.styles)

    def get_embedding(self, text):
        try:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=[text]
            )
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            print(f"[ERROR] Error generating embedding: {e}")
            return None

    def analyze(self, tweets, account):
        analysis_results = []
        for tweet in tweets:
            content = tweet.get('content', '').strip()[:512]

            if not content:
                print(f"[WARNING] Tweet content is empty for tweet: {tweet}")
                continue

            try:
                sentiment = self.sentiment_analyzer(content)[0]
            except Exception as e:
                print(f"[ERROR] Error during sentiment analysis: {e}")
                sentiment = {'label': 'neutral', 'score': 0.0}

            result = {
                'content': content,
                'engagement': tweet.get('engagement', 0),
                'sentiment': sentiment['label'],
                'score': sentiment['score']
            }
            analysis_results.append(result)

            vector_id = hashlib.md5(content.encode('utf-8')).hexdigest()
            embedding = self.get_embedding(content)

            if embedding:
                try:
                    self.index.upsert([
                        (vector_id, embedding, {
                            'sentiment': sentiment['label'],
                            'style': self.get_random_style(),
                            'engagement': tweet.get('engagement', 0),
                            'account': account,
                            'content': content
                        })
                    ])
                except Exception as e:
                    print(f"[ERROR] Error upserting to Pinecone: {e}")

        return analysis_results

    def get_recent_analysis(self, account):
        try:
            filter = {"account": {"$eq": account}}
            
            result = self.index.query(
                vector=[0.0] * 1536,
                top_k=5,
                include_metadata=True,
                filter=filter
            )
            
            analysis_results = []
            for match in result.matches:
                content = match.metadata.get('content', '')
                if not content:
                    print(f"[WARNING] Empty content in Pinecone match: {match.metadata}")

                analysis_results.append({
                    'content': content,
                    'engagement': match.metadata.get('engagement', 0),
                    'sentiment': match.metadata.get('sentiment', ''),
                    'style': match.metadata.get('style', '')
                })
            
            return analysis_results
        except Exception as e:
            print(f"[ERROR] Error querying Pinecone: {e}")
            return []

    def update_with_feedback(self, engagement_data):
        print("\n[INFO] Updating Pinecone with feedback...")
        
        for data in engagement_data:
            try:
                tweet_id = data.get('tweet_id', '')
                likes = data.get('likes', 0)
                retweets = data.get('retweets', 0)

                if not isinstance(tweet_id, str) or not tweet_id:
                    raise ValueError(f"[ERROR] Invalid tweet_id: {tweet_id}")
                if not isinstance(likes, int) or not isinstance(retweets, int):
                    raise ValueError(f"[ERROR] Engagement metrics must be integers: Likes={likes}, Retweets={retweets}")

                print(f"[DEBUG] Updating tweet ID: {tweet_id}, Likes: {likes}, Retweets: {retweets}")
                self.index.update(tweet_id, {
                    'likes': likes,
                    'retweets': retweets
                })
                print(f"[INFO] Successfully updated Pinecone for tweet ID: {tweet_id}")

            except Exception as e:
                print(f"[ERROR] Error updating Pinecone for tweet ID {tweet_id}: {e}")
