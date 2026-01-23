import os
import asyncio
from dotenv import load_dotenv

# LangChain Imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

# Load Keys
load_dotenv()

class SchoolAgent:
    def __init__(self):
        # 1. Initialize the Database (Using the OpenAI Embeddings we just created)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.db = Chroma(persist_directory="./data/chroma_db", embedding_function=self.embeddings)
        
        # 2. Initialize the LLMs
        self.llm_openai = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    async def _get_llm_response_stream(self, llm, name, prompt):
        """Helper to call an LLM asynchronously with streaming support."""
        try:
            chunks = []
            async for chunk in llm.astream(prompt):
                chunks.append(chunk.content)
            full_response = "".join(chunks)
            return {"name": name, "answer": full_response, "chunks": chunks}
        except Exception as e:
            error_msg = f"API Error: {str(e)}"
            return {"name": name, "answer": error_msg, "chunks": [error_msg]}

    async def ask(self, question: str):
        # 1. Retrieve MORE chunks from ChromaDB for better context (increase from 3 to 6)
        print(f"🔍 Searching database for: {question}")
        docs = self.db.similarity_search(question, k=6)
        
        if not docs:
            print("⚠️ WARNING: No documents found in vector database!")
            context = "No relevant information found in the database."
        else:
            context = "\n\n---\n\n".join([d.page_content for d in docs])
            print(f"✅ Retrieved {len(docs)} relevant chunks")
            # Debug: Print first 200 chars of context
            print(f"📄 Context preview: {context[:200]}...")

        # 2. Improved System Prompt with STRICT instructions
        template = """You are the Official Sunmarke School Admissions Assistant. 
Your goal is to provide accurate, helpful, and warm guidance to parents.

CONTEXT FROM SCHOOL DATABASE:
{context}

USER QUESTION: {question}

CRITICAL INSTRUCTIONS:
1. CAREFULLY READ the context above - it contains information from the Sunmarke School website.
2. If the answer IS in the context, provide a detailed, helpful response based ONLY on that information.
3. Be specific with numbers, dates, and details when they are provided in the context.
4. If the answer is NOT in the context, politely say: "I don't have that specific information in my database. Please contact the admissions office at admissions@sunmarke.com or call +971 4 xxx xxxx for accurate details."
5. Keep the tone professional yet welcoming and friendly.
6. If the question is completely unrelated to Sunmarke School or education, politely redirect them to ask about the school.

ANSWER (Be helpful, specific, and use the context provided):
"""
        
        prompt = ChatPromptTemplate.from_template(template).format(
            context=context, 
            question=question
        )

        # 3. Fire all active LLMs in Parallel with streaming
        print(f"🧠 Polling LLMs in parallel...")
        tasks = [
            self._get_llm_response_stream(self.llm_openai, "OpenAI (GPT-4o)", prompt),
            self._get_llm_response_stream(self.llm_gemini, "Google Gemini", prompt),
        ]
        
        results = await asyncio.gather(*tasks)
        return results

# For testing this file independently
if __name__ == "__main__":
    agent = SchoolAgent()
    user_query = "What are the school fees for Year 1?"
    
    async def test_run():
        responses = await agent.ask(user_query)
        for r in responses:
            print(f"\n{'='*60}")
            print(f"--- {r['name']} ---")
            print('='*60)
            print(r['answer'])
            print()

    asyncio.run(test_run())