"""RAG Reliability AI Agent: Exactly four LangGraph nodes in sequential order."""

# ==========================================
# IMPORTS: LANGGRAPH AND LANGCHAIN TOOLS
# ==========================================

import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from tools.document_search_tool import search_documents
from tools.relevance_check_tool import check_relevance
from tools.answer_generation_tool import generate_answer
from tools.answer_verification_tool import verify_answer

load_dotenv()


# ==========================================
# LLM
# Purpose: Initialize OpenAI in backend.py
# Used by: relevance, generation, verification tools
# ==========================================

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0
)


# ==========================================
# SECTION 1: LANGGRAPH STATE
# Class: RAGState
# Purpose: Share data between all graph nodes
# ==========================================

class RAGState(TypedDict):
    question: str
    retrieved_documents: list[dict]
    relevant_documents: list[dict]
    draft_answer: str
    verification: dict
    trace: list[dict]


# ==========================================
# SECTION 2: LANGGRAPH NODE 1
# Function: document_search_node()
# Tool: search_documents()
# ==========================================

def document_search_node(state: RAGState) -> dict:
    documents = search_documents(state["question"])
    return {
        "retrieved_documents": documents,
        "trace": state["trace"] + [{
            "node": "document_search",
            "result": f"{len(documents)} chunks retrieved"
        }]
    }


# ==========================================
# SECTION 3: LANGGRAPH NODE 2
# Function: relevance_check_node()
# Tool: check_relevance()
# ==========================================

def relevance_check_node(state: RAGState) -> dict:
    documents = check_relevance(state["question"], state["retrieved_documents"], llm)
    return {
        "relevant_documents": documents,
        "trace": state["trace"] + [{
            "node": "relevance_check",
            "result": f"{len(documents)} relevant chunks"
        }]
    }


# ==========================================
# SECTION 4: LANGGRAPH NODE 3
# Function: answer_generation_node()
# Tool: generate_answer()
# ==========================================

def answer_generation_node(state: RAGState) -> dict:
    answer = generate_answer(state["question"], state["relevant_documents"], llm)
    return {
        "draft_answer": answer,
        "trace": state["trace"] + [{
            "node": "answer_generation",
            "result": "Draft answer generated"
        }]
    }


# ==========================================
# SECTION 5: LANGGRAPH NODE 4
# Function: answer_verification_node()
# Tool: verify_answer()
# ==========================================

def answer_verification_node(state: RAGState) -> dict:
    verification = verify_answer(
        state["question"], state["draft_answer"], state["relevant_documents"], llm
    )
    return {
        "verification": verification,
        "trace": state["trace"] + [{
            "node": "answer_verification",
            "result": verification["reason"]
        }]
    }


# ==========================================
# SECTION 6: LANGGRAPH WORKFLOW
# Nodes: 4, execution order fixed by add_edge()
# ==========================================

graph = StateGraph(RAGState)

graph.add_node("document_search", document_search_node)
graph.add_node("relevance_check", relevance_check_node)
graph.add_node("answer_generation", answer_generation_node)
graph.add_node("answer_verification", answer_verification_node)

graph.add_edge(START, "document_search")
graph.add_edge("document_search", "relevance_check")
graph.add_edge("relevance_check", "answer_generation")
graph.add_edge("answer_generation", "answer_verification")
graph.add_edge("answer_verification", END)

rag_graph = graph.compile()


# ==========================================
# SECTION 7: FASTAPI TO LANGGRAPH CONNECTION
# Function: run_rag_agent()
# Called by: app.py -> ask()
# FastAPI Endpoint: POST /api/ask (defined in app.py)
# Purpose: Run compiled LangGraph for one question
# Note: This function is NOT a FastAPI endpoint.
# ==========================================

def run_rag_agent(question: str) -> dict:
    """Run one question through four nodes and return verified evidence."""

    initial_state: RAGState = {
        "question": question,
        "retrieved_documents": [],
        "relevant_documents": [],
        "draft_answer": "",
        "verification": {},
        "trace": [],
    }

    result = rag_graph.invoke(initial_state)
    verification = result["verification"]

    return {
        "question": question,
        "answer": verification["answer"],
        "verified": verification["verified"],
        "verification_reason": verification["reason"],
        "sources": [
            {
                "id": document["id"],
                "source": document["source"],
                "score": document["score"],
                "text": document["text"],
            }
            for document in result["relevant_documents"]
        ],
        "retrieved_count": len(result["retrieved_documents"]),
        "relevant_count": len(result["relevant_documents"]),
        "trace": result["trace"],
    }
