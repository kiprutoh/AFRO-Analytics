"""
Automatic LLM-based Translation System
Uses OpenRouter API to translate website content automatically
"""

import os
import json
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class AutoTranslator:
    """Automatic translation using LLM"""
    
    def __init__(self):
        """Initialize the translator"""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.cache_file = "translation_cache.json"
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load translation cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save translation cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def translate(self, text: str, target_language: str, context: str = "") -> str:
        """
        Translate text to target language using LLM
        
        Args:
            text: Text to translate
            target_language: Target language (English, Portuguese, French)
            context: Optional context about the text (e.g., "health data dashboard")
            
        Returns:
            Translated text
        """
        # Return original if already in English
        if target_language.lower() == "english":
            return text
        
        # Check cache first
        cache_key = f"{text}_{target_language}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # If no API key, return original
        if not self.api_key:
            print("Warning: No OPENROUTER_API_KEY found. Returning original text.")
            return text
        
        # Language mapping
        lang_map = {
            "portuguese": "Portuguese (Portugal)",
            "french": "French"
        }
        
        target = lang_map.get(target_language.lower(), target_language)
        
        # Create translation prompt
        prompt = f"""Translate the following text from English to {target}.

Context: This is from a {context if context else 'health data analytics dashboard for WHO AFRO region'}.

IMPORTANT RULES:
1. Maintain technical terminology accuracy
2. Keep medical/health terms precise
3. Preserve any numbers, dates, or codes exactly as they are
4. Keep proper nouns (country names, organization names) unchanged
5. Maintain formatting (line breaks, punctuation)
6. If text contains HTML or markdown, preserve the syntax
7. Be natural and professional

Text to translate:
{text}

Translation:"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/afro-analytics",
                "X-Title": "AFRO Analytics Translation"
            }
            
            data = {
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                translation = result['choices'][0]['message']['content'].strip()
                
                # Cache the translation
                self.cache[cache_key] = translation
                self._save_cache()
                
                return translation
            else:
                print(f"Translation API error: {response.status_code}")
                return text
                
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def translate_dict(self, translations_dict: Dict, target_language: str) -> Dict:
        """
        Translate all values in a dictionary
        
        Args:
            translations_dict: Dictionary with English text values
            target_language: Target language
            
        Returns:
            Dictionary with translated values
        """
        if target_language.lower() == "english":
            return translations_dict
        
        translated = {}
        total = len(translations_dict)
        
        print(f"Translating {total} items to {target_language}...")
        
        for i, (key, value) in enumerate(translations_dict.items(), 1):
            if isinstance(value, str):
                translated[key] = self.translate(value, target_language)
                print(f"  [{i}/{total}] {key}: {value[:50]}... -> {translated[key][:50]}...")
            else:
                translated[key] = value
        
        return translated
    
    def get_cached_translation(self, text: str, target_language: str) -> Optional[str]:
        """Get translation from cache if available"""
        cache_key = f"{text}_{target_language}"
        return self.cache.get(cache_key)
    
    def clear_cache(self):
        """Clear translation cache"""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("Translation cache cleared")


# Global translator instance
_translator = None


def get_translator() -> AutoTranslator:
    """Get or create global translator instance"""
    global _translator
    if _translator is None:
        _translator = AutoTranslator()
    return _translator


def auto_translate(text: str, target_language: str, context: str = "") -> str:
    """
    Convenience function to translate text
    
    Args:
        text: Text to translate
        target_language: Target language
        context: Optional context
        
    Returns:
        Translated text
    """
    translator = get_translator()
    return translator.translate(text, target_language, context)


if __name__ == "__main__":
    # Test the translator
    translator = AutoTranslator()
    
    print("Testing Auto Translator")
    print("="*80)
    
    # Test Portuguese
    test_text = "Welcome to the AFRO Regional Data Hub"
    print(f"\nOriginal: {test_text}")
    print(f"Portuguese: {translator.translate(test_text, 'Portuguese')}")
    print(f"French: {translator.translate(test_text, 'French')}")
    
    # Test with medical context
    test_medical = "Treatment Success Rate"
    print(f"\nOriginal: {test_medical}")
    print(f"Portuguese: {translator.translate(test_medical, 'Portuguese', 'TB outcomes dashboard')}")
    print(f"French: {translator.translate(test_medical, 'French', 'TB outcomes dashboard')}")
    
    print("\n✅ Translation test complete!")

