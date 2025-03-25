from langchain.llms.base import LLM
from typing import Optional, List, Any
from pydantic import Field 


class GroqLangChainWrapper(LLM):
    groq_client: Any = Field(..., exclude=True)
    model_name: str
    
    class Config:
        arbitrary_types_allowed = True  # Allows Any type in pydantic models
    
    @property
    def _llm_type(self) -> str:
        """A short string identifying the type of LLM."""
        return "groq"
    
    def _call(self, promt: str, stop: Optional[List[str]] = None) -> str:
        """
        This method is called by LangChain when it needs to generate text.
        It must return a string with the model's output.
        """
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant whom translate questions into SQL queries. The database contains geodata and you might need to use postGIS. Return only the query and the result."},
                    {"role": "user", "content": promt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling Groq: {e}"
        