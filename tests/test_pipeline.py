import unittest
from unittest.mock import patch
from mock_data import MOCK_CHUNKS, MOCK_RETRIEVED, MOCK_ANSWER
import pipeline

PAGES = [{"text": c["text"], "source": c["source"], "page": c["page"]} for c in MOCK_CHUNKS]


class TestPrepareDocument(unittest.TestCase):
    @patch("pipeline.build_index", return_value="INDEX")
    @patch("pipeline.chunk_documents", return_value=MOCK_CHUNKS)
    @patch("pipeline.load_pdf", return_value=PAGES)
    def test_returns_index_and_chunks(self, load_pdf, chunk_documents, build_index):
        index, chunks = pipeline.prepare_document(b"%PDF", "sample_course.pdf")
        self.assertEqual((index, chunks), ("INDEX", MOCK_CHUNKS))
        load_pdf.assert_called_once_with(b"%PDF", "sample_course.pdf")
        build_index.assert_called_once_with(MOCK_CHUNKS)

    @patch("pipeline.chunk_documents", return_value=[])
    @patch("pipeline.load_pdf", return_value=[])
    def test_no_text_raises(self, *_):
        with self.assertRaises(ValueError):
            pipeline.prepare_document(b"%PDF", "scanned.pdf")

    def test_empty_file_raises(self):
        with self.assertRaises(ValueError):
            pipeline.prepare_document(b"", "empty.pdf")


@patch("pipeline.retrieve", return_value=MOCK_RETRIEVED)
class TestAnswerQuestion(unittest.TestCase):
    @patch("pipeline.generate_answer", return_value=MOCK_ANSWER)
    def test_contract_keys(self, generate_answer, retrieve):
        result = pipeline.answer_question("What is self-attention?", "INDEX", MOCK_CHUNKS, k=5)
        retrieve.assert_called_once_with("What is self-attention?", "INDEX", MOCK_CHUNKS, k=5)
        generate_answer.assert_called_once_with("What is self-attention?", MOCK_RETRIEVED)
        self.assertEqual(result["answer"], MOCK_ANSWER["answer"])
        self.assertEqual(result["sources"], MOCK_ANSWER["sources"])
        self.assertEqual(result["passages"], MOCK_RETRIEVED)
        for src in result["sources"]:
            self.assertEqual(set(src), {"chunk_id", "source", "page"})

    @patch("pipeline.generate_answer", return_value={
        "answer": "<think>maybe [c0002]?</think>\nSelf-attention mixes tokens [c0001].",
        "sources": [{"chunk_id": "c0001", "source": "sample_course.pdf", "page": 12},
                    {"chunk_id": "c0002", "source": "sample_course.pdf", "page": 15}]})
    def test_strips_think_and_its_citations(self, *_):
        result = pipeline.answer_question("q", "INDEX", MOCK_CHUNKS)
        self.assertEqual(result["answer"], "Self-attention mixes tokens [c0001].")
        self.assertEqual([s["chunk_id"] for s in result["sources"]], ["c0001"])


if __name__ == "__main__":
    unittest.main()
