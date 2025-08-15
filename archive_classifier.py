import os
import logging
from dotenv import load_dotenv
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("OpenRouterMetadataWorkflow")


class ArchiveClassifier:
    def __init__(self, model: str = "perplexity/sonar"):
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logger.error("OPENROUTER_API_KEY not found in environment variables.")
            raise EnvironmentError("Missing OpenRouter API key.")

        self.api_key = api_key
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        logger.info("OpenRouter client initialized.")

    def build_query(self, topics_list_str: str) -> str:
        logger.debug(f"Building query for topic: {topics_list_str}")
        return f"""
            You are a scientific research assistant. Classify each of the following topics into one of:
            arXiv, PubMed, bioRxiv, ChemRxiv.

            - arXiv: physics, mathematics, computer science, statistics, quantitative biology, etc.
            - PubMed: peer-reviewed biomedical and clinical research (e.g., medicine, health, pharmacology).
            - bioRxiv: life sciences and biology preprints (e.g., genomics, neuroscience, molecular biology).
            - ChemRxiv: chemistry preprints (e.g., organic, inorganic, physical, analytical chemistry).

            Topics:
            {topics_list_str}

            Return ONLY a valid JSON object where:
            - Each key is the topic exactly as given
            - Each value is one of: arXiv, PubMed, bioRxiv, ChemRxiv

            Example:
            {{
                "graph neural networks for traffic prediction": "arXiv",
                "randomized controlled trial of a new antihypertensive drug": "PubMed"
            }}
            """

    def run(self, topic: str):
        query = self.build_query(topic)
        logger.info(f"Sending query for topic: {topic}")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload
            )

            if response.status_code != 200:
                logger.error("API Error %d: %s", response.status_code, response.text)
                return ""

            result = response.json()
            logger.info("Query completed successfully.")
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Failed to query OpenRouter: {e}")
            raise
