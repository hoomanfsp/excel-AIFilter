import json
import time
import asyncio
from openai import OpenAI
from tenacity import retry, wait_exponential, stop_after_attempt

class OpenAIFilter:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        # OpenAI paid tier rate limits are generally much higher than free tiers (e.g., 500 RPM / 10k TPM).
        # We can run batches extremely quickly.
        self.rate_limit_delay = 0.5  
        
    def _create_prompt(self, items: list[str], topic: str) -> str:
        prompt = f"Evaluate the following items against the topic: '{topic}'.\n"
        prompt += f"Return a JSON array of exactly {len(items)} integers where 1 means the item matches the topic conceptually or factually, and 0 means it does not.\n"
        prompt += "Output exactly a JSON array like [1, 0, 1] with nothing else.\n\n"
        prompt += "Items to evaluate:\n"
        for i, item in enumerate(items):
            prompt += f"{i+1}. {item}\n"
        return prompt

    @retry(wait=wait_exponential(multiplier=2, min=2, max=60), stop=stop_after_attempt(5))
    def filter_batch(self, items: list[str], topic: str) -> list[int]:
        if not items:
            return []
            
        prompt = self._create_prompt(items, topic)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        try:
            content = response.choices[0].message.content.strip()
            
            # Handle potential markdown blocks and conversational text
            import re
            match = re.search(r'\[(.*?)\]', content, re.DOTALL)
            if match:
                content = match.group(0)
            else:
                raise ValueError("No JSON array found in the response")
            
            # Parse the JSON response
            result = json.loads(content)
            
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
            
        except Exception as e:
            print(f"Error parsing response: {e}. Raw content: {response.choices[0].message.content}")
            raise  # trigger retry

    async def filter_all_async(self, all_items: list[str], topic: str, batch_size: int, progress_callback=None) -> list[int]:
        results = []
        total_items = len(all_items)
        
        for i in range(0, total_items, batch_size):
            start_time = time.time()
            
            batch = all_items[i:i+batch_size]
            
            batch_result = await asyncio.to_thread(self.filter_batch, batch, topic)
            results.extend(batch_result)
            
            if progress_callback:
                progress_callback(min(i + batch_size, total_items), total_items)
            
            # Rate limiting delay
            elapsed = time.time() - start_time
            if (i + batch_size) < total_items and elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
                
        return results
