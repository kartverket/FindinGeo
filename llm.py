from langchain_community.llms import HuggingFaceHub
from config import HF_API_KEY, HF_REPO_ID

def llm_hf():
    return HuggingFaceHub(
        repo_id=HF_REPO_ID,
        model_kwargs={"temperature": 0.0},
        huggingfacehub_api_token=HF_API_KEY
    )
    
    