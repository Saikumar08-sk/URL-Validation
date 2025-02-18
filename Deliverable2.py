import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

class URLValidator:
    """
    URL Validator class that evaluates the credibility of a webpage
    using domain trust, content relevance, fact-checking, bias detection, and citations.
    """

    def __init__(self):
        # Load models once to avoid redundant API calls
        self.similarity_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.fake_news_classifier = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-fake-news-detection")
        self.sentiment_analyzer = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment")

    def fetch_page_content(self, url: str) -> str:
        """ Fetches and extracts text content from the given URL. """
        try:
            headers = {"User-Agent": "Mozilla/5.0"}  # Helps bypass some bot protections
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            content = " ".join([p.text for p in soup.find_all("p")])
            return content if content else "Error: No readable content found on the page."
        except requests.exceptions.Timeout:
            return "Error: Request timed out."
        except requests.exceptions.HTTPError as e:
            return f"Error: HTTP {e.response.status_code} - Page may not exist."
        except requests.exceptions.RequestException as e:
            return f"Error: Unable to fetch URL ({str(e)})."

    def get_domain_trust(self, url: str, content: str) -> int:
        """ Simulated function to assess domain trust. """
        if "Error" in content:
            return 0
        return len(url) % 5 + 1  # Mock trust rating (1-5)

    def compute_similarity_score(self, user_query: str, content: str) -> int:
        """ Computes semantic similarity between user query and page content. """
        if "Error" in content:
            return 0
        return int(util.pytorch_cos_sim(
            self.similarity_model.encode(user_query),
            self.similarity_model.encode(content)
        ).item() * 100)

    def check_facts(self, content: str) -> int:
        """ Simulated function to check fact reliability. """
        if "Error" in content:
            return 0
        return len(content) % 5 + 1  # Mock fact-check rating (1-5)

    def detect_bias(self, content: str) -> int:
        """ Uses NLP sentiment analysis to detect potential bias in content. """
        if "Error" in content:
            return 0
        sentiment_result = self.sentiment_analyzer(content[:512])[0]
        return 100 if sentiment_result["label"] == "POSITIVE" else 50 if sentiment_result["label"] == "NEUTRAL" else 30

    def get_star_rating(self, score: float) -> tuple:
        """ Converts a score (0-100) into a 1-5 star rating. """
        stars = max(1, min(5, round(score / 20)))  # Normalize 100-scale to 5-star scale
        return stars, "⭐" * stars

    def generate_explanation(self, domain_trust, similarity_score, fact_check_score, bias_score, final_score) -> str:
        """ Generates a human-readable explanation for the score. """
        reasons = []
        if domain_trust < 50:
            reasons.append("The source has low domain authority.")
        if similarity_score < 50:
            reasons.append("The content is not highly relevant to your query.")
        if fact_check_score < 50:
            reasons.append("Limited fact-checking verification found.")
        if bias_score < 50:
            reasons.append("Potential bias detected in the content.")

        return " ".join(reasons) if reasons else "This source is highly credible and relevant."

    def rate_url_validity(self, user_query: str, url: str):
        """ Main function to evaluate the validity of a webpage. """
        content = self.fetch_page_content(url)

        # Handle errors
        if "Error" in content:
            return {"Validation Error": content}

        domain_trust = self.get_domain_trust(url, content)
        similarity_score = self.compute_similarity_score(user_query, content)
        fact_check_score = self.check_facts(content)
        bias_score = self.detect_bias(content)

        final_score = (
            (0.3 * domain_trust) +
            (0.3 * similarity_score) +
            (0.2 * fact_check_score) +
            (0.2 * bias_score)
        )

        stars, icon = self.get_star_rating(final_score)
        explanation = self.generate_explanation(domain_trust, similarity_score, fact_check_score, bias_score, final_score)

        return {
            "raw_score": {  
                "Domain Trust": domain_trust,
                "Content Relevance": similarity_score,
                "Fact-Check Score": fact_check_score,
                "Bias Score": bias_score,
                "Final Validity Score": final_score
            },
            "stars": {
                "icon": icon
            },
            "explanation": explanation
        }
