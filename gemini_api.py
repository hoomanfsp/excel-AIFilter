import json
import time
import asyncio
from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt

class GeminiFilter:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        self.rate_limit_delay = 15.0  # Free tier limit is 5 requests per minute -> 1 request per 12 seconds + buffer
        
    def _create_prompt(self, items: list[str], topic: str) -> str:
        prompt = f"Evaluate the following items against the topic: '{topic}'.\n"
        prompt += f"Return a JSON array of exactly {len(items)} integers where 1 means the item matches the topic conceptually or factually, and 0 means it does not.\n"
        prompt += "Output exactly a JSON array like [1, 0, 1] with nothing else.\n\n"
        prompt += "Items to evaluate:\n"
        for i, item in enumerate(items):
            prompt += f"{i+1}. {item}\n"
        return prompt

    @retry(wait=wait_exponential(multiplier=2, min=4, max=60), stop=stop_after_attempt(5))
    def filter_batch(self, items: list[str], topic: str) -> list[int]:
        if not items:
            return []
            
        prompt = self._create_prompt(items, topic)
        
        # We use gemini-2.5-flash as the default fast/cheap model for these kinds of tasks
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        
        # Parse the JSON response
        result = json.loads(response.text)
        
        # Basic validation
        if not isinstance(result, list):
            raise ValueError("Response is not a list")
            
        # If length mismatch, pad or truncate
        if len(result) < len(items):
            result.extend([0] * (len(items) - len(result)))
        elif len(result) > len(items):
            result = result[:len(items)]
            
        # Ensure elements are 0 or 1
        result = [1 if x else 0 for x in result]
        
        return result
    async def filter_all_async(self, all_items: list[str], topic: str, batch_size: int, progress_callback=None) -> list[int]:
        results = []
        total_items = len(all_items)
        
        for i in range(0, total_items, batch_size):
            start_time = time.time()
            
            batch = all_items[i:i+batch_size]
            
            # Since the google-genai library supports both sync and async, but we have a sync wrapper 
            # for simplicity we'll just run it in a thread or we can block inside the async loop
            # Here we just run the sync method, blocking the worker thread is fine since we do it sequentially 
            # due to strict rate limits.
            batch_result = await asyncio.to_thread(self.filter_batch, batch, topic)
            results.extend(batch_result)
            
            if progress_callback:
                progress_callback(min(i + batch_size, total_items), total_items)
            
            # Rate limiting delay
            elapsed = time.time() - start_time
            if (i + batch_size) < total_items and elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
                
        return results
