import asyncio, sys
sys.path.insert(0, './backend')

async def test():
    import google.generativeai as genai
    import os
    
    api_key = os.environ.get('GEMINI_API_KEY', '')
    print('Local GEMINI_API_KEY:', 'SET' if api_key else 'MISSING')
    
    if not api_key:
        print('Skipping local test - no local key.')
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = 'Return a JSON array with one fact object: [{"statement": "Test works", "category": "General", "confidence": 0.9}]'
    
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"temperature": 0.1}
        )
        print('Response text:', response.text[:300])
        print('Finish reason:', response.candidates[0].finish_reason if response.candidates else 'N/A')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')

asyncio.run(test())
