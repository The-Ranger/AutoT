import schedule
import time
from tweet_collector import TweetCollector
from tweet_analyzer import TweetAnalyzer
from tweet_generator import TweetGenerator
from tweet_scheduler import TweetScheduler
import config

class BabyAGI:
    def __init__(self):
        self.collector = TweetCollector()
        self.analyzer = TweetAnalyzer()
        self.generator = TweetGenerator()
        self.scheduler = TweetScheduler()

    def collect_and_analyze_tweets(self):
        """Collects and analyzes tweets."""
        print("\n[INFO] Starting tweet collection and analysis...")
        for account in config.TARGET_ACCOUNTS:
            print(f"[INFO] Collecting tweets for '{account}'...")
            tweets = self.collector.scrape_tweets(account)
            print(f"[INFO] Collected {len(tweets)} tweets from '{account}'.")

            print("[INFO] Analyzing tweets...")
            analysis_results = self.analyzer.analyze(tweets, account)
            print(f"[INFO] Analysis complete. {len(analysis_results)} tweets analyzed.")

    def generate_and_schedule_tweets(self):
            print("\n[INFO] Starting tweet generation and scheduling...")
            for account in config.TARGET_ACCOUNTS:
                print(f"[INFO] Fetching recent analysis for '{account}'...")
                analysis_results = self.analyzer.get_recent_analysis(account)  # No need to pass top_k or recent_hours

                if not analysis_results:
                    print(f"[WARNING] No recent analysis found for '{account}'. Skipping tweet generation.")
                    continue

                generated_tweets = []
                for analysis in analysis_results:
                    tweet_content = self.generator.generate_tweet(
                        analysis_context=analysis.get('content', ''),
                        style=analysis.get('style', 'neutral'),
                        trending_topics=self.analyzer.get_trending_topics()
                    )
                    generated_tweets.append(tweet_content)

                self.scheduler.schedule_tweets(generated_tweets)
                print(f"[INFO] {len(generated_tweets)} tweets generated for '{account}'.")
                                
    def monitor_engagement(self):
        """Monitors engagement of posted tweets and updates feedback."""
        print("\n[INFO] Monitoring engagement...")
        engagement_data = self.scheduler.monitor_engagement()
        if engagement_data:
            print(f"[INFO] Engagement data received: {engagement_data}")
            self.analyzer.update_with_feedback(engagement_data)
        else:
            print("[INFO] No engagement data found.")

    def run(self):
        """Runs the main loop for collecting, analyzing, generating, and scheduling tweets."""
        # Initial run of tasks for immediate execution
        print("\n[INFO] Running initial tasks...")
        self.collect_and_analyze_tweets()
        self.generate_and_schedule_tweets()
        self.monitor_engagement()

        # Schedule tweet collection and analysis
        schedule.every(config.COLLECTION_INTERVAL).minutes.do(self.collect_and_analyze_tweets)
        
        # Schedule tweet generation
        schedule.every(config.GENERATION_INTERVAL).minutes.do(self.generate_and_schedule_tweets)
        
        # Schedule engagement monitoring
        schedule.every(config.ENGAGEMENT_MONITOR_INTERVAL).minutes.do(self.monitor_engagement)
        
        # Schedule tweet posting at specific times
        for post_time in config.POSTING_TIMES:
            schedule.every().day.at(post_time).do(self.scheduler.post_scheduled_tweets)

        print("[INFO] BabyAGI is running and scheduled tasks are set up.")
        
        # Main loop to run scheduled tasks
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("[INFO] Stopping BabyAGI...")
        finally:
            self.collector.close()  # Ensure WebDriver is closed when the program terminates
