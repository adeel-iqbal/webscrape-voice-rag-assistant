import os
import asyncio
from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Load API Keys
load_dotenv()

async def main():
    # 1. Verified URLs
    urls = [
        "https://www.sunmarke.com/",
        "https://www.sunmarke.com/admissions/tuition-fees/",
        "https://www.sunmarke.com/for-parents/school-timings/",
        "https://www.sunmarke.com/for-parents/academic-calendar/",
        "https://www.sunmarke.com/faqs/",
        "https://www.sunmarke.com/contact-us/",
        "https://www.sunmarke.com/learning/primary/our-curriculum-primary/",
        "https://www.sunmarke.com/learning/secondary/our-curriculum-secondary/",
        "https://www.sunmarke.com/learning/sixth-form/a-levels/",
        "https://www.sunmarke.com/learning/sixth-form/ib-diploma-programme-ibdp/",
        "https://www.sunmarke.com/signature-programmes/steam-design-thinking/",
        "https://www.sunmarke.com/about/principals-message/",
        "https://www.sunmarke.com/about/academic-results/",
        "https://www.sunmarke.com/for-parents/transport-services/",
        "https://www.sunmarke.com/for-parents/dining-catering/"
    ]
    
    print("🚀 Starting the crawler (Fresh Start)...")
    
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(cache_mode=True) 

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for url in urls:
            print(f"📄 Scraping: {url}")
            result = await crawler.arun(url=url, config=run_cfg)
            
            if result.success:
                content = result.markdown
                chunks = text_splitter.split_text(content)
                all_chunks.extend(chunks)
                print(f"✅ Extracted {len(chunks)} chunks from {url}")
            else:
                print(f"❌ Failed to crawl {url}: {result.error_message}")

    # 2. Setup OpenAI Embeddings (Fresh DB)
    print("🧠 Initializing OpenAI Embeddings...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 3. Create ChromaDB
    persist_directory = "./data/chroma_db"
    print(f"📦 Storing {len(all_chunks)} chunks into ChromaDB at {persist_directory}...")
    
    # This will create the folder automatically
    vectorstore = Chroma.from_texts(
        texts=all_chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print(f"✨ Ingestion complete! {len(all_chunks)} segments stored successfully.")

if __name__ == "__main__":
    asyncio.run(main())