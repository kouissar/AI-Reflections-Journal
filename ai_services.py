import logging
import random
from langchain.llms import Ollama
from langchain_groq import ChatGroq
import streamlit as st
from langchain.prompts import PromptTemplate
import os

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, provider="ollama"):
        try:
            self.provider = provider
            if provider == "ollama":
                self.llm = Ollama(
                    model="llama3.2:1b",
                    base_url="http://localhost:11434",
                )
            elif provider == "groq":
                groq_api_key = st.secrets.get("llm", {}).get("groq_api_key", "")
                print(groq_api_key)
                if not groq_api_key:
                    raise ValueError("Groq API key not found in secrets")
                self.llm = ChatGroq(
                    api_key=groq_api_key,
                    model_name="llama3-8b-8192"
                )
            logger.info(f"AI Service initialized successfully with {provider}")
        except Exception as e:
            logger.error(f"Error initializing AI service: {str(e)}")
            self.llm = None

    def generate_daily_quote(self):
        try:
            if not self.llm:
                raise Exception("LLM not initialized")

            prompt = PromptTemplate(
                input_variables=[],
                template="""Generate an inspiring and thoughtful quote about self-reflection, mindfulness, or personal growth. 
                The quote should be brief (max 2 sentences) and include the author. 
                Format: "Quote" - Author"""
            )
            
            response = self.llm.invoke(prompt.format())
            # Handle different response types
            if hasattr(response, 'content'):  # ChatMessage object from Groq
                return response.content.strip()
            return response.strip()  # String from Ollama
            
        except Exception as e:
            logger.error(f"Error generating quote: {str(e)}")
            fallback_quotes = [
                '"The only journey is the one within." - Rainer Maria Rilke',
                '"Know thyself." - Socrates',
                '"Self-awareness is the key to self-mastery." - Gretchen Rubin',
                '"Reflection is the lamp of the heart." - Al-Ghazali'
            ]
            return random.choice(fallback_quotes)

    def analyze_entry(self, content, mood, mood_factors):
        try:
            if not self.llm:
                raise Exception("LLM not initialized")

            prompt = PromptTemplate(
                input_variables=["content", "mood", "factors"],
                template="""Act as an empathetic therapist or personal development coach. 
                Analyze the following journal entry and provide thoughtful insights, validation, 
                and gentle suggestions for growth (2-3 sentences max).

                Journal Entry: {content}
                Mood Level (1-5): {mood}
                Influencing Factors: {factors}

                Provide your response in this format:
                🤔 [Your therapeutic insight and suggestion here]"""
            )
            
            response = self.llm.invoke(
                prompt.format(
                    content=content,
                    mood=mood,
                    factors=mood_factors if mood_factors else "None specified"
                )
            )
            # Handle different response types
            if hasattr(response, 'content'):  # ChatMessage object from Groq
                return response.content.strip()
            return response.strip()  # String from Ollama
            
        except Exception as e:
            logger.error(f"Error analyzing entry: {str(e)}")
            return "I'm currently unable to provide insights, but I appreciate you sharing your thoughts. Consider reflecting on what you've written and be kind to yourself. 🌱"