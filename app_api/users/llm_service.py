from groq import Groq
from datetime import datetime
import logging
import os
from typing import Dict, List, Optional, Generator

class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        # Get API key from parameter, environment variable, or use default
        if api_key:
            self.api_key = api_key
        elif os.getenv("GROQ_API_KEY"):
            self.api_key = os.getenv("GROQ_API_KEY")
        else:
            # Fallback to your hardcoded key (consider removing this in production)
            self.api_key = "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"
        
        try:
            # Initialize client with API key
            self.client = Groq(api_key=self.api_key)
            self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
            self.temperature = 0.85
            self.max_tokens = 1024
            self._test_connection()
        except Exception as e:
            logging.error(f"Failed to initialize LLM service: {str(e)}")
            raise

    def _test_connection(self):
        """Test the connection to the LLM service"""
        try:
            # Test with a simple non-streaming request
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                model=self.model,
                max_completion_tokens=10,
                temperature=0.1,
                stream=False
            )
            if not response.choices:
                raise ConnectionError("No response from API")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to LLM service: {str(e)}")

    def _format_chat_history(self, history: List[Dict], system_prompt: str) -> List[Dict]:
        """Format chat history into the required format for the API"""
        formatted_history = []
        
        # Always start with the system prompt
        if system_prompt.strip():
            formatted_history.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation history
        for msg in history:
            if isinstance(msg, dict) and 'content' in msg and 'isUser' in msg:
                if msg["content"].strip():  # Only add non-empty messages
                    formatted_history.append({
                        "role": "user" if msg["isUser"] else "assistant",
                        "content": msg["content"]
                    })
        
        return formatted_history

    def get_response(self,
                    message: str,
                    system_prompt: str = "You are a helpful assistant.",
                    chat_history: Optional[List[Dict]] = None,
                    stream: bool = False) -> Dict:
        """
        Get response from LLM service
        
        Args:
            message (str): User's message
            system_prompt (str): System prompt to set the AI's behavior
            chat_history (Optional[List[Dict]]): Previous chat history
            stream (bool): Whether to use streaming response
        """
        try:
            if not message.strip():
                return {
                    'error': 'Empty message',
                    'timestamp': datetime.now().strftime("%H:%M"),
                    'status': 'error'
                }

            # Prepare messages with provided system prompt
            messages = self._format_chat_history(chat_history or [], system_prompt)
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })

            if stream:
                return self._get_streaming_response(messages)
            else:
                return self._get_standard_response(messages)

        except Exception as e:
            logging.error(f"Error getting LLM response: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().strftime("%H:%M"),
                'status': 'error'
            }

    def _get_standard_response(self, messages: List[Dict]) -> Dict:
        """Get a standard (non-streaming) response"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_completion_tokens=self.max_tokens,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            if not chat_completion.choices or not chat_completion.choices[0].message:
                raise ValueError("No valid response from LLM service")
            
            response = chat_completion.choices[0].message.content
            
            return {
                'response': response,
                'timestamp': datetime.now().strftime("%H:%M"),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")

    def _get_streaming_response(self, messages: List[Dict]) -> Dict:
        """Get a streaming response"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_completion_tokens=self.max_tokens,
                top_p=1,
                stream=True,
                stop=None,
            )
            
            return {
                'stream': chat_completion,
                'timestamp': datetime.now().strftime("%H:%M"),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Streaming API call failed: {str(e)}")

    def get_streaming_response(self,
                             message: str,
                             system_prompt: str = "You are a helpful assistant.",
                             chat_history: Optional[List[Dict]] = None) -> Generator[str, None, None]:
        """
        Get streaming response as a generator
        
        Args:
            message (str): User's message
            system_prompt (str): System prompt to set the AI's behavior
            chat_history (Optional[List[Dict]]): Previous chat history
            
        Yields:
            str: Chunks of the response as they arrive
        """
        try:
            if not message.strip():
                yield "Error: Empty message"
                return

            # Prepare messages
            messages = self._format_chat_history(chat_history or [], system_prompt)
            messages.append({
                "role": "user",
                "content": message
            })

            # Get streaming completion
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_completion_tokens=self.max_tokens,
                top_p=1,
                stream=True,
                stop=None,
            )
            
            # Yield chunks as they arrive
            for chunk in chat_completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logging.error(f"Error in streaming response: {str(e)}")
            yield f"Error: {str(e)}"

# Example usage:
if __name__ == "__main__":
    # Initialize the service
    llm = LLMService(api_key="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")
    
    # Standard response
    result = llm.get_response("Hello, how are you?")
    if result['status'] == 'success':
        print("Standard response:", result['response'])
    else:
        print("Error:", result['error'])
    
    # Streaming response
    print("\nStreaming response:")
    for chunk in llm.get_streaming_response("Tell me a short story"):
        print(chunk, end="", flush=True)
    print()  # New line after streaming