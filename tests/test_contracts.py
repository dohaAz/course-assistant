import unittest
from chunking import chunk_documents

class TestChunkContract(unittest.TestCase):
    def test_chunk_structure_and_pages(self):
        docs = [{"text": "a " * 450, "source": "one.pdf", "page": 2},
                {"text": "b " * 200, "source": "one.pdf", "page": 3}]
        chunks = chunk_documents(docs, chunk_size=150, overlap=20)
        self.assertTrue(chunks)
        self.assertTrue(all(set(x) == {"chunk_id", "text", "source", "page"} for x in chunks))
        self.assertTrue(all(x["page"] in (2,3) for x in chunks))
        self.assertEqual(len({x["chunk_id"] for x in chunks}), len(chunks))

    def test_empty(self):
        self.assertEqual(chunk_documents([]), [])

if __name__ == "__main__":
    unittest.main()
