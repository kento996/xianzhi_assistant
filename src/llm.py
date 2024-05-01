from google.generativeai.types import HarmCategory, HarmBlockThreshold
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
def get_gemini_pro_15() -> BaseChatModel:

    return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest",
                                  temperature=0,
                                  convert_system_message_to_human=True,
                                  transport="rest",
                                  safety_settings={
                                      HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                                      HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                                      HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                                      HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,

                                  }
                                  )

def get_gemini_pro() -> BaseChatModel:


    return ChatGoogleGenerativeAI(model="gemini-pro",
                                  temperature=0,
                                  convert_system_message_to_human=True,
                                  transport="rest",
                                  safety_settings={
                                      HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                                      HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                                      HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                                      HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,

                                  })

def get_gemini_embedding():
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001",
                                         transport="rest")


