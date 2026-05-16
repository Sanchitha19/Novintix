import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from dotenv import load_dotenv
load_dotenv()

def get_llm():
    api_key = os.getenv("XAI_API_KEY")
    if api_key and api_key.startswith("gsk_"):
        # It's a Groq key
        return ChatOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile"
        )
    elif api_key:
        # Assume it's an xAI key
        return ChatOpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            model="grok-beta"
        )
    else:
        # Fallback to OpenAI if configured
        return ChatOpenAI(model="gpt-4o")

def invoke_llm(system_prompt: str, context: str, query: str, history: list = []):
    llm = get_llm()
    messages = [SystemMessage(content=system_prompt)]
    
    # Add history
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
            
    # Add the final query with context
    final_content = f"Context:\n{context}\n\nCustomer Question: {query}"
    messages.append(HumanMessage(content=final_content))
    
    response = llm.invoke(messages)
    return response.content
