"""
FAQ chatbot engine.
Loads the FAQs, vectorizes them (TF-IDF) after NLP preprocessing,
and answers a user question via cosine similarity.
"""
import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocessing import preprocess

DEFAULT_FAQ_PATH = Path(__file__).parent / "data" / "faqs.json"
CONFIDENCE_THRESHOLD = 0.25  # below this score, we consider there is no good answer

FALLBACK_ANSWER = (
    "I'm not sure I understand your question. "
    "Could you rephrase it, or contact our support at support@example.com?"
)


class FAQChatbot:
    def __init__(self, faq_path: Path = DEFAULT_FAQ_PATH):
        self.faq_path = faq_path
        self.faqs = self._load_faqs(faq_path)
        self.questions = [item["question"] for item in self.faqs]
        self.answers = [item["answer"] for item in self.faqs]

        # NLP preprocessing of all FAQ questions
        self._preprocessed_questions = [preprocess(q) for q in self.questions]

        # Two combined vectorizers for more robust matching:
        # - word_vectorizer: captures meaning via words/lemmas (precise, but rigid with synonyms)
        # - char_vectorizer: captures close morphological variants
        #   (e.g. "pay" / "payment") via character n-grams
        # The final score is the average of both similarities, which reduces
        # false positives that either vectorizer alone would produce.
        self.word_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.word_matrix = self.word_vectorizer.fit_transform(self._preprocessed_questions)

        self.char_vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
        self.char_matrix = self.char_vectorizer.fit_transform(self._preprocessed_questions)

    @staticmethod
    def _load_faqs(path: Path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_response(self, user_question: str):
        """
        Returns (answer, matched_question, score) for the user question.
        If no sufficient match is found, returns the default fallback answer.
        """
        if not user_question or not user_question.strip():
            return "Please ask a question.", None, 0.0

        processed = preprocess(user_question)
        if not processed:
            return FALLBACK_ANSWER, None, 0.0

        similarities = self._hybrid_similarities(processed)

        best_idx = similarities.argmax()
        best_score = float(similarities[best_idx])

        if best_score < CONFIDENCE_THRESHOLD:
            return FALLBACK_ANSWER, None, best_score

        return self.answers[best_idx], self.questions[best_idx], best_score

    def _hybrid_similarities(self, processed_text: str):
        word_vec = self.word_vectorizer.transform([processed_text])
        char_vec = self.char_vectorizer.transform([processed_text])

        word_sims = cosine_similarity(word_vec, self.word_matrix)[0]
        char_sims = cosine_similarity(char_vec, self.char_matrix)[0]

        return 0.5 * word_sims + 0.5 * char_sims

    def top_matches(self, user_question: str, k: int = 3):
        """Returns the top k matches (useful for debugging/testing)."""
        processed = preprocess(user_question)
        similarities = self._hybrid_similarities(processed)
        top_idx = similarities.argsort()[::-1][:k]
        return [
            {"question": self.questions[i], "answer": self.answers[i], "score": float(similarities[i])}
            for i in top_idx
        ]


if __name__ == "__main__":
    # Simple CLI mode for quick testing without Streamlit
    bot = FAQChatbot()
    print("=== FAQ Chatbot (CLI) — type 'quit' to exit ===")
    while True:
        q = input("\nYou: ")
        if q.strip().lower() in {"quit", "exit"}:
            break
        answer, matched, score = bot.get_response(q)
        print(f"Bot ({score:.2f}): {answer}")
