
import json

with open("data/chunks_test.json", encoding="utf-8") as f:
    chunks = json.load(f)

required = {"chunk_id", "text", "source", "page"}

assert len(chunks) > 0, "No chunks found"
assert all(required.issubset(c) for c in chunks), "Missing fields"
assert all(c["text"].strip() for c in chunks), "Empty text"
assert all(isinstance(c["page"], int) and c["page"] >= 1 for c in chunks)

ids = [c["chunk_id"] for c in chunks]
assert len(ids) == len(set(ids)), "Duplicate chunk IDs"

print("All validations passed!")
print("Total chunks:", len(chunks))
print("Sources:", set(c["source"] for c in chunks))
print("Pages:", sorted(set(c["page"] for c in chunks)))
