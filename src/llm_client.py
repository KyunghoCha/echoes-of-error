"""
Ollama LLM Client with retry logic and JSON parsing.
"""
import json
import time
import re
import requests
from typing import Optional, Dict, Any
from src.config import OLLAMA_BASE_URL, MODEL_NAME


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(
        self, 
        base_url: str = OLLAMA_BASE_URL, 
        model: str = MODEL_NAME,
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
        seed: Optional[int] = None,
        json_schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for role conditioning
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict containing 'response' (raw text) and 'parsed' (JSON if valid)
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if seed is not None:
            payload["options"]["seed"] = seed
            
        if json_schema:
            payload["format"] = json_schema
        else:
            # Force JSON mode by default for reliability
            payload["format"] = "json"
        
        if system_prompt:
            payload["system"] = system_prompt
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url, 
                    json=payload, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                raw_response = result.get("response", "")
                
                # Try to parse as JSON
                parsed = self._parse_json_response(raw_response)
                
                return {
                    "response": raw_response,
                    "parsed": parsed,
                    "success": parsed is not None,
                    "model": self.model,
                    "attempt": attempt + 1
                }
                
            except requests.exceptions.Timeout as e:
                last_error = f"Timeout after {self.timeout}s"
                print(f"[Attempt {attempt + 1}] {last_error}")
                
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {e}"
                print(f"[Attempt {attempt + 1}] {last_error}")
                
            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {e}"
                print(f"[Attempt {attempt + 1}] {last_error}")
                
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                print(f"[Attempt {attempt + 1}] {last_error}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))
        
        return {
            "response": None,
            "parsed": None,
            "success": False,
            "error": last_error,
            "model": self.model,
            "attempt": self.max_retries
        }
    
    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract and parse JSON from LLM response.
        Handles cases where JSON is wrapped in markdown code blocks.
        """
        if not text:
            return None
            
        # Try direct JSON parse first
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
            r'```\s*([\s\S]*?)\s*```',       # ``` ... ```
            r'\{[\s\S]*\}',                   # Raw JSON object
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    return json.loads(json_str.strip())
                except (json.JSONDecodeError, IndexError):
                    continue
        
        return None
    
    def health_check(self) -> bool:
        """Check if Ollama server is running and model is available."""
        try:
            # Check if server is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            # Check if model is available
            models = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]
            
            if self.model.split(":")[0] in model_names:
                return True
            else:
                print(f"Model '{self.model}' not found. Available: {model_names}")
                return False
                
        except Exception as e:
            print(f"Health check failed: {e}")
            return False


def test_client():
    """Simple test for the Ollama client."""
    client = OllamaClient()
    
    print("=== Ollama Client Test ===")
    print(f"Base URL: {client.base_url}")
    print(f"Model: {client.model}")
    
    # Health check
    print("\n1. Health Check...")
    if client.health_check():
        print("   ✓ Server is running and model is available")
    else:
        print("   ✗ Health check failed")
        return
    
    # Simple generation test
    print("\n2. Generation Test...")
    result = client.generate(
        prompt="Say 'Hello' in JSON format: {\"message\": \"...\"}",
        temperature=0.1
    )
    
    if result["success"]:
        print(f"   ✓ Generation successful")
        print(f"   Response: {result['parsed']}")
    else:
        print(f"   ✗ Generation failed: {result.get('error', 'Unknown error')}")
        print(f"   Raw response: {result['response']}")


if __name__ == "__main__":
    test_client()
