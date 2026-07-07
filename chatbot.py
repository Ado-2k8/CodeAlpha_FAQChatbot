"""
Moteur du chatbot FAQ.
Charge les FAQ, les vectorise (TF-IDF) après préprocessing NLP,
et répond à une question utilisateur via similarité cosinus.
"""
import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocessing import preprocess

DEFAULT_FAQ_PATH = Path(__file__).parent / "data" / "faqs.json"
CONFIDENCE_THRESHOLD = 0.25  # en dessous de ce score, on considère qu'on n'a pas de bonne réponse

FALLBACK_ANSWER = (
    "Je ne suis pas sûr de comprendre votre question. "
    "Pourriez-vous la reformuler, ou contacter notre support à support@example.com ?"
)


class FAQChatbot:
    def __init__(self, faq_path: Path = DEFAULT_FAQ_PATH):
        self.faq_path = faq_path
        self.faqs = self._load_faqs(faq_path)
        self.questions = [item["question"] for item in self.faqs]
        self.answers = [item["answer"] for item in self.faqs]

        # Préprocessing NLP de toutes les questions FAQ
        self._preprocessed_questions = [preprocess(q) for q in self.questions]

        # Deux vectoriseurs combinés pour un matching plus robuste :
        # - word_vectorizer : capture le sens via les mots/lemmes (précis, mais rigide face aux synonymes)
        # - char_vectorizer : capture les variantes morphologiques proches
        #   (ex: "pay" / "payment") via des n-grammes de caractères
        # Le score final est la moyenne des deux similarités, ce qui réduit
        # les faux positifs qu'un seul des deux vectoriseurs produirait isolément.
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
        Retourne (answer, matched_question, score) pour la question utilisateur.
        Si aucune correspondance suffisante n'est trouvée, renvoie la réponse par défaut.
        """
        if not user_question or not user_question.strip():
            return "Veuillez poser une question.", None, 0.0

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
        """Retourne les k meilleures correspondances (utile pour debug/tests)."""
        processed = preprocess(user_question)
        similarities = self._hybrid_similarities(processed)
        top_idx = similarities.argsort()[::-1][:k]
        return [
            {"question": self.questions[i], "answer": self.answers[i], "score": float(similarities[i])}
            for i in top_idx
        ]


if __name__ == "__main__":
    # Mode CLI simple pour tester rapidement sans Streamlit
    bot = FAQChatbot()
    print("=== Chatbot FAQ (CLI) — tapez 'quit' pour quitter ===")
    while True:
        q = input("\nVous: ")
        if q.strip().lower() in {"quit", "exit"}:
            break
        answer, matched, score = bot.get_response(q)
        print(f"Bot ({score:.2f}): {answer}")
