"""Tool 2: grade retrieved context for relevance using an LLM."""
import json
from langchain_core.messages import SystemMessage, HumanMessage

def check_relevance(question: str, documents: list[dict], llm) -> list[dict]:
    relevant = []
    for doc in documents:
        prompt = f"Question: {question}\nDocument excerpt: {doc['text'][:2500]}"
        result = llm.invoke([SystemMessage(content="Is this excerpt useful to answer the question? Respond with ONLY YES or NO."), HumanMessage(content=prompt)])
        if result.content.strip().upper().startswith("YES"):
            relevant.append(doc)
    return relevant
