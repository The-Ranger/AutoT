import openai
from langchain.llms import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import the available error classes from the main openai module
from openai import Timeout, APIError, RateLimitError

# Override the retry logic in LangChain's OpenAI integration
def patched_completion_with_retry(llm, prompt, **params):
    retry_decorator = retry(
        reraise=True,
        stop=stop_after_attempt(6),
        wait=wait_exponential(min=1, max=60),
        retry=(retry_if_exception_type(Timeout)
               | retry_if_exception_type(APIError)
               | retry_if_exception_type(RateLimitError)),
    )
    return retry_decorator(llm.completion)(prompt=prompt, **params)

# Patch the LangChain OpenAI integration
OpenAI.completion_with_retry = patched_completion_with_retry
