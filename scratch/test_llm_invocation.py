import asyncio
import os

async def test_llm():
    from agents.faq_agent import FAQAgent
    from models.schemas import Query, TraceContext
    agent = FAQAgent()
    
    import utils.llm
    
    # Patch LLM to log when called
    original_invoke = utils.llm.invoke_llm
    call_count = 0
    
    def logged_invoke(prompt, context, query, history):
        nonlocal call_count
        call_count += 1
        print(f'LLM CALLED — call #{call_count}')
        print(f'Prompt length: {len(str(prompt))} chars')
        result = original_invoke(prompt, context, query, history)
        print(f'LLM Response length: {len(result)} chars')
        return result
    
    utils.llm.invoke_llm = logged_invoke
    
    query = Query(user_id="user_1", text='I could not place an order, why?', session_id="123")
    query.metadata["context"] = {'customer_id': 1, 'orders': [], 'rag_docs': []}
    
    response = await agent.process(query)
    
    print(f'Final response: {response.response_text[:200]}')
    
    if call_count == 0:
        print('CRITICAL FAIL: LLM was never called — agent is using hardcoded responses')
    else:
        print(f'PASS: LLM was called {call_count} time(s)')

asyncio.run(test_llm())
