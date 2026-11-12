"""Tool 4: check support; reject answers with unsupported claims."""
from langchain_core.messages import SystemMessage, HumanMessage

def verify_answer(question: str, answer: str, documents: list[dict], llm) -> dict:
    if not documents:
        return {"verified": False, "reason": "No relevant evidence", "answer": answer}
    context = "\n".join(f"[{d['source']}:{d['id']}] {d['text']}" for d in documents)
    prompt = f"QUESTION: {question}\nANSWER: {answer}\nSOURCES:\n{context}"
    response = llm.invoke([SystemMessage(content="Check whether EVERY factual claim in ANSWER is supported by SOURCES and all cited IDs exist. Reply ONLY VERIFIED or UNSUPPORTED, followed by one short reason."), HumanMessage(content=prompt)])
    verdict = str(response.content).strip()
    verified = verdict.upper().startswith("VERIFIED")
    return {"verified": verified, "reason": verdict, "answer": answer if verified else "I cannot verify the proposed answer against the uploaded documents. Please review the retrieved evidence."}
