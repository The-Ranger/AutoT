import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import config

class TweetGenerator:
    def __init__(self):
        self.client = openai.Client(api_key=config.OPENAI_API_KEY)

    @retry(
        reraise=True,
        stop=stop_after_attempt(6),
        wait=wait_exponential(min=1, max=60),
        retry=(
            retry_if_exception_type(openai.Timeout)
            | retry_if_exception_type(openai.APIError)
            | retry_if_exception_type(openai.RateLimitError)
        )
    )
    def generate_tweet(self, analysis_context, style, trending_topics):
        """
        Generates a tweet based on recent analysis context, style, and trending topics.
        """

        prompt = (
            f"Generate a tweet in the style of {style}.\n"
            f"Consider the following trending topics: {', '.join(trending_topics)}.\n"
            f"Based on recent analysis: {analysis_context}\n"
        )

        # Output the prompt for debugging
        print(f"[DEBUG] Prompt to OpenAI: {prompt}")

        try:
            # Call OpenAI's newer Client API for chat completions
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a tweet generator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=280,  # Adjust as needed
                temperature=0.7
            )

            tweet_content = response.choices[0].message.content.strip()

            # Return the tweet content as a dictionary to maintain compatibility
            return {"content": tweet_content}

        except (openai.Timeout, openai.APIError, openai.RateLimitError) as e:
            print(f"[ERROR] Error generating tweet: {e}")
            return {"content": "Error in tweet generation."}
