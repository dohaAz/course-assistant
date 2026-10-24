import unittest
from mock_data import MOCK_CHUNKS
from retriever import build_index, retrieve

REAL = [
    {"chunk_id": "c0001", "source": "course.pdf", "page": 12,
     "text": "Self-attention allows each token to attend to all other tokens in the sequence."},
    {"chunk_id": "c0002", "source": "course.pdf", "page": 20,
     "text": "La descente de gradient met à jour les poids dans la direction opposée au gradient de la fonction de coût."},
    {"chunk_id": "c0003", "source": "course.pdf", "page": 31,
     "text": "FAISS permet la recherche de plus proches voisins sur des vecteurs denses."},
    {"chunk_id": "c0004", "source": "course.pdf", "page": 40,
     "text": "Le surapprentissage se produit quand le modèle mémorise les données d'entraînement au lieu de généraliser."},
]


class TestRetrieverContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):                      # le modèle ne se charge qu'une fois
        cls.mock_index = build_index(MOCK_CHUNKS)
        cls.index = build_index(REAL)

    def test_result_structure(self):
        res = retrieve("What does self-attention do?", self.mock_index, MOCK_CHUNKS, k=3)
        self.assertEqual(len(res), 2)         # 2 chunks seulement -> 2 résultats
        for r in res:
            self.assertEqual(set(r), {"chunk_id", "text", "source", "page", "score"})
            self.assertIsInstance(r["score"], float)
            self.assertIsInstance(r["page"], int)
        scores = [r["score"] for r in res]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_metadata_copied_not_invented(self):
        res = retrieve("token order", self.mock_index, MOCK_CHUNKS, k=2)
        by_id = {c["chunk_id"]: c for c in MOCK_CHUNKS}
        for r in res:
            c = by_id[r["chunk_id"]]
            self.assertEqual((r["text"], r["source"], r["page"]), (c["text"], c["source"], c["page"]))

    def test_relevance_fr_and_cross_lingual(self):
        top = lambda q: retrieve(q, self.index, REAL, k=1)[0]["chunk_id"]
        self.assertEqual(top("Comment fonctionne la descente de gradient ?"), "c0002")
        self.assertEqual(top("What is overfitting? The model memorizes the training data"), "c0004")         # question EN, chunk FR

    def test_edge_cases(self):
        self.assertEqual(retrieve("", self.index, REAL), [])
        self.assertEqual(retrieve("question", None, REAL), [])
        self.assertIsNone(build_index([]))
        self.assertEqual(len(retrieve("gradient", self.index, REAL, k=50)), 4)


if __name__ == "__main__":
    unittest.main()