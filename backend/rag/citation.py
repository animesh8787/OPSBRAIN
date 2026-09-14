import re


def extract_and_verify_citations(
    answer: str,
    retrieved_chunks: list,
) -> tuple[str, list[dict]]:
    """
    Extract [n] markers from the answer, map each to the corresponding
    retrieved chunk (1-indexed position in retrieved_chunks), and return
    (cleaned_answer, citations). Any [n] with no matching chunk is stripped
    from the answer text rather than left as a broken/dangling reference -
    this must never surface an unverified citation live during a demo.
    """
    pattern = re.compile(r"\[(\d+)\]")
    citations = []
    seen_indices = set()

    def replace_or_strip(match: re.Match) -> str:
        n = int(match.group(1))
        idx = n - 1
        if 0 <= idx < len(retrieved_chunks):
            if n not in seen_indices:
                chunk = retrieved_chunks[idx]
                citations.append({
                    "index": n,
                    "chunk_id": str(chunk.chunk_id),
                    "document_id": str(chunk.document_id),
                    "document_filename": chunk.document_filename,
                    "page_number": chunk.page_number,
                    "content": chunk.content,
                    "score": chunk.score,
                    "citation_verified": True,
                })
                seen_indices.add(n)
            return match.group(0)  # keep the [n] marker in the text
        return ""  # strip unverified marker entirely

    cleaned_answer = pattern.sub(replace_or_strip, answer)
    # Collapse any double spaces left behind by stripped markers.
    cleaned_answer = re.sub(r"  +", " ", cleaned_answer).strip()

    citations.sort(key=lambda c: c["index"])
    return cleaned_answer, citations
