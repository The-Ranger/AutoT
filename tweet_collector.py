from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import config

class TweetCollector:
    def __init__(self):
        # Set up Chrome options
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--user-data-dir=C:\Development\chrome_profile")
        
        # Initialize ChromeDriver with service
        service = Service(executable_path=config.CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # Wait up to 10 seconds

    def convert_engagement(self, engagement_str):
        """
        Converts engagement strings like '312K' or '4.4M' to integers.
        """
        if 'K' in engagement_str:
            return int(float(engagement_str.replace('K', '').replace(',', '')) * 1_000)
        elif 'M' in engagement_str:
            return int(float(engagement_str.replace('M', '').replace(',', '')) * 1_000_000)
        else:
            return int(engagement_str.replace(',', ''))

    def scrape_tweets(self, account, scroll_count=3):
        """
        Collects tweets from a specified Twitter account, with improved XPaths and error handling.
        
        Args:
            account (str): Twitter username without '@' symbol.
            scroll_count (int): Number of times to scroll to load more tweets.

        Returns:
            list: A list of dictionaries with tweet content and engagement metrics.
        """
        # Navigate to the user's Twitter page
        self.driver.get(f'{config.TWITTER_URL}/{account}')
        sleep(2)  # Allow page to load

        tweets = []
        for _ in range(scroll_count):
            # Wait for tweet elements to load on the page
            try:
                tweet_elements = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//article[@data-testid='tweet']"))
                )
            except Exception as e:
                print(f"Error locating tweet elements: {e}")
                continue

            for element in tweet_elements:
                try:
                    # Extract tweet content using the new class
                    try:
                        content_element = element.find_element(By.XPATH, ".//div[contains(@class, 'css-175oi2r')]")
                        content = content_element.text
                    except:
                        content = "[No content found]"

                    # Extract like count with an updated XPath
                    try:
                        like_element = element.find_element(By.XPATH, ".//button[@data-testid='like']//span")
                        engagement_str = like_element.text or '0'
                        engagement = self.convert_engagement(engagement_str)
                    except:
                        engagement = 0  # Default to 0 if the like count is not found

                    tweets.append({'content': content, 'engagement': engagement})
                except Exception as e:
                    print(f"Error scraping tweet: {e}")
                    continue

            # Scroll down to load additional tweets
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)  # Wait for tweets to load after scrolling

        return tweets

    def close(self):
        """Close the WebDriver session."""
        self.driver.quit()
