"""LLM Integration Module for CollectiveBrain

Provides dynamic LLM-driven objective decomposition using GitHub Models API.
Falls back to OpenAI or stub mode if not configured.
"""

import os
import json
from typing import List, Dict, Any, Optional

# Try to import httpx for API calls
try:
    import httpx
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False


class LLMClient:
    """Unified LLM client supporting multiple providers."""
    
    PROVIDERS = {
        "github": {
            "base_url": "https://models.inference.ai.azure.com/chat/completions",
            "model": "gpt-4o-mini",
            "requires": "GITHUB_TOKEN"
        },
        "openai": {
            "base_url": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-4o-mini",
            "requires": "OPENAI_API_KEY"
        },
        "azure": {
            "base_url": None,  # Set via AZURE_OPENAI_ENDPOINT
            "model": None,
            "requires": "AZURE_OPENAI_API_KEY"
        }
    }
    
    def __init__(self, provider: str = None):
        """Initialize LLM client with specified or auto-detected provider."""
        self.provider = provider or os.getenv("LLM_PROVIDER", "github")
        self._api_key = None
        self._base_url = None
        self._model = None
        self._configure()
    
    def _configure(self):
        """Configure client based on provider."""
        config = self.PROVIDERS.get(self.provider, self.PROVIDERS["github"])
        
        if self.provider == "github":
            self._api_key = os.getenv("GITHUB_TOKEN")
            self._base_url = config["base_url"]
            self._model = os.getenv("GITHUB_MODEL", config["model"])
        elif self.provider == "openai":
            self._api_key = os.getenv("OPENAI_API_KEY")
            self._base_url = os.getenv("OPENAI_BASE_URL", config["base_url"])
            self._model = os.getenv("OPENAI_MODEL", config["model"])
        elif self.provider == "azure":
            self._api_key = os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
            deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
            version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
            self._base_url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version={version}"
            self._model = deployment
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available and configured."""
        return HTTP_AVAILABLE and bool(self._api_key)
    
    def complete(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """
        Send a chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional API parameters
        
        Returns:
            Assistant response text or None on failure
        """
        if not self.is_available:
            return None
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.provider == "azure":
            headers["api-key"] = self._api_key
        else:
            headers["Authorization"] = f"Bearer {self._api_key}"
        
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000)
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self._base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[LLM] API error: {e}")
            return None


def decompose_with_llm(objective: str, max_goals: int = 5) -> List[str]:
    """
    Use LLM to decompose an objective into actionable sub-goals.
    
    Args:
        objective: The high-level objective to decompose
        max_goals: Maximum number of sub-goals
    
    Returns:
        List of sub-goal strings
    """
    client = LLMClient()
    
    if not client.is_available:
        # Fallback to template-based decomposition
        return _fallback_decomposition(objective)
    
    system_prompt = """You are an expert project decomposer for a multi-agent AI system.
Your task is to break down objectives into 3-5 distinct, actionable sub-goals.

Rules:
1. Each sub-goal should be specific and actionable
2. Sub-goals should cover different aspects: research, design, implementation, testing
3. Return ONLY a JSON array of strings, no other text
4. Keep each sub-goal concise (under 100 characters)

Example output:
["Research existing solutions", "Design system architecture", "Implement core modules", "Write tests", "Document the API"]"""

    user_prompt = f"Decompose this objective into {max_goals} sub-goals:\n\n{objective}"
    
    response = client.complete([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    if response:
        try:
            # Parse JSON array from response
            # Handle potential markdown code blocks
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
            goals = json.loads(clean)
            if isinstance(goals, list) and all(isinstance(g, str) for g in goals):
                return goals[:max_goals]
        except (json.JSONDecodeError, IndexError):
            pass
    
    return _fallback_decomposition(objective)


def _fallback_decomposition(objective: str) -> List[str]:
    """Template-based decomposition when LLM is unavailable."""
    return [
        f"Research requirements for: {objective}",
        f"Design architecture for: {objective}",
        f"Create implementation plan for: {objective}",
        f"Develop and test: {objective}",
        f"Document and deploy: {objective}"
    ]


def generate_worker_response(role: str, task: str) -> str:
    """
    Generate a worker response using LLM.
    
    Args:
        role: Worker role (e.g., 'Research', 'Finance')
        task: Task description
    
    Returns:
        Generated response or fallback
    """
    client = LLMClient()
    
    if not client.is_available:
        return f"[{role}] Completed analysis for: {task}"
    
    system_prompt = f"""You are a specialized AI worker with the role: {role}.
Provide a brief, professional response to the assigned task.
Keep your response under 200 characters and action-oriented."""

    response = client.complete([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Complete this task: {task}"}
    ], max_tokens=100)
    
    return response or f"[{role}] Completed analysis for: {task}"


if __name__ == "__main__":
    # Test LLM integration
    print("Testing LLM Integration...")
    
    client = LLMClient()
    print(f"Provider: {client.provider}")
    print(f"Available: {client.is_available}")
    
    if client.is_available:
        goals = decompose_with_llm("Build a real-time chat application")
        print("\nDecomposed goals:")
        for i, g in enumerate(goals, 1):
            print(f"  {i}. {g}")
    else:
        print("\nNo API key configured. Using fallback decomposition.")
        goals = decompose_with_llm("Test objective")
        for i, g in enumerate(goals, 1):
            print(f"  {i}. {g}")
