from langchain_community.llms import HuggingFaceHub
from config import HF_API_KEY, HF_REPO_ID
from langchain_huggingface import HuggingFaceEndpoint
from custom_huggingface_endpoint import CustomHuggingFaceEndpoint

# def llm_hf():
#     return HuggingFaceEndpoint(
#         repo_id=HF_REPO_ID,
#         #model_kwargs={"temperature": 0.0},
#         huggingfacehub_api_token=HF_API_KEY
#     )
    
    
# Basic Example (no streaming)  
# llm = HuggingFaceEndpoint(  
# repo_id=HF_REPO_ID, 
# max_new_tokens=250,
# #max_new_tokens=512,  
# #top_k=10,  
# #top_p=0.95,  
# #typical_p=0.95,  
# # temperature=0.01,  
# # repetition_penalty=1.03,  
# huggingfacehub_api_token=HF_API_KEY  
# )  
# print(llm.invoke("when was ChatGPT created?"))  



# initialize Hub LLM
llm = CustomHuggingFaceEndpoint(
    max_new_tokens=250,
    repo_id=HF_REPO_ID,
    temperature=0,
    repetition_penalty=1.03,
    huggingfacehub_api_token=HF_API_KEY,
    
)

print(llm.invoke("What is Deep Learning?", stop=None, watermark=None, return_full_text=None, stop_sequences=None))