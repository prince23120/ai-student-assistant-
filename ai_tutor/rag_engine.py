import math
import re
from collections import Counter
from .models import DocumentChunk
from .services import get_ai_tutor_response

def tokenize(text):
    return re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())

def retrieve_relevant_chunks(document, query, top_k=4):
    """
    Retrieves the top_k most relevant chunks from document using BM25 / TF-IDF ranking.
    """
    chunks = list(document.chunks.all())
    if not chunks:
        return []

    query_tokens = tokenize(query)
    if not query_tokens:
        return chunks[:top_k]

    # Calculate document frequencies
    total_chunks = len(chunks)
    doc_freq = Counter()
    chunk_tokens_list = []

    for chunk in chunks:
        tokens = tokenize(chunk.content)
        chunk_tokens_list.append(tokens)
        unique_tokens = set(tokens)
        for token in unique_tokens:
            doc_freq[token] += 1

    # Score each chunk
    scored_chunks = []
    avg_len = sum(len(t) for t in chunk_tokens_list) / max(1, total_chunks)
    k1 = 1.5
    b = 0.75

    for idx, chunk in enumerate(chunks):
        tokens = chunk_tokens_list[idx]
        chunk_len = len(tokens)
        score = 0.0
        token_counts = Counter(tokens)

        for q_term in query_tokens:
            if q_term in token_counts:
                # IDF
                df = doc_freq[q_term]
                idf = math.log((total_chunks - df + 0.5) / (df + 0.5) + 1.0)
                # BM25 TF
                tf = token_counts[q_term]
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (chunk_len / avg_len))
                score += idf * (numerator / denominator)

        # Small boost for earlier chunks/introduction
        score += max(0, (total_chunks - chunk.chunk_index) / (total_chunks * 10))
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k]]


def ask_document_rag(document, user_query, conversation):
    """
    Executes RAG pipeline:
    1. Retrieve relevant chunks
    2. Build context-enriched prompt
    3. Generate AI response with page citations
    """
    relevant_chunks = retrieve_relevant_chunks(document, user_query, top_k=4)

    context_str = ""
    citations = []
    for c in relevant_chunks:
        context_str += f"\n--- [Document: {document.title} | Page/Slide {c.page_number}] ---\n{c.content}\n"
        citations.append({
            'page_number': c.page_number,
            'excerpt': c.content[:160] + "..."
        })

    rag_prompt = (
        f"You are answering questions specifically from the uploaded study material: '{document.title}'.\n\n"
        f"CONTEXT RETRIEVED FROM DOCUMENT:\n{context_str}\n\n"
        f"STUDENT QUESTION:\n{user_query}\n\n"
        f"INSTRUCTIONS:\n"
        f"1. Base your answer strictly on the context provided above.\n"
        f"2. Cite the exact page or slide number using [Page X] or [Slide Y] whenever stating a fact.\n"
        f"3. If the document does not contain enough information to answer completely, state what is mentioned in the document and supplement with academic guidance.\n"
        f"4. Format your answer with clean Markdown, bold highlights, and bullet points."
    )

    response_text = get_ai_tutor_response(conversation, rag_prompt)
    return response_text, citations


def generate_document_summary(document, conversation):
    """
    Generates a high-level summary of the document using the initial chunks.
    """
    chunks = list(document.chunks.all()[:6])
    combined_text = "\n\n".join([c.content for c in chunks])[:3500]

    prompt = (
        f"Please provide an executive academic summary of this study material: '{document.title}'.\n\n"
        f"EXCERPT CONTENT:\n{combined_text}\n\n"
        f"Format as:\n"
        f"### 📄 Document Summary: {document.title}\n"
        f"- **Core Purpose & Theme** (2-3 sentences)\n"
        f"- **Key Concepts Covered** (4-6 crisp bullet points)\n"
        f"- **Suggested Exam Focus Areas**\n"
    )
    return get_ai_tutor_response(conversation, prompt)


def generate_document_mcqs(document, conversation, count=5):
    """
    Generates practice MCQs from the document content.
    """
    chunks = list(document.chunks.all()[:8])
    combined_text = "\n\n".join([c.content for c in chunks])[:3500]

    prompt = (
        f"Generate {count} multiple-choice examination questions based on this study material: '{document.title}'.\n\n"
        f"DOCUMENT CONTENT:\n{combined_text}\n\n"
        f"For each question, provide:\n"
        f"1. Clear Question text with page reference if applicable\n"
        f"2. 4 Options: A), B), C), D)\n"
        f"3. Correct Option\n"
        f"4. Brief Explanation of why that option is correct."
    )
    return get_ai_tutor_response(conversation, prompt)


def generate_document_notes(document, conversation):
    """
    Generates concise revision notes from the document.
    """
    chunks = list(document.chunks.all()[:8])
    combined_text = "\n\n".join([c.content for c in chunks])[:3500]

    prompt = (
        f"Generate structured revision study notes from this document: '{document.title}'.\n\n"
        f"DOCUMENT CONTENT:\n{combined_text}\n\n"
        f"Format as high-yield revision notes with definitions, key formulas, diagrams description, and critical exam points."
    )
    return get_ai_tutor_response(conversation, prompt)
