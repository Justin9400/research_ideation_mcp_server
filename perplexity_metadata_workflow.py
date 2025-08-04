import os
import logging
from dotenv import load_dotenv
from perplexipy import PerplexityClient

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("PerplexityMetadataWorkflow")

# --- Perplexity Wrapper Class ---
class PerplexityMetadataWorkflow:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            logger.error("PERPLEXITY_API_KEY not found in environment variables.")
            raise EnvironmentError("Missing Perplexity API key.")
        self.client = PerplexityClient(api_key)
        logger.info("Perplexity client initialized.")

    def build_query(self, archive: str, topic: str) -> str:
        logger.debug(f"Building query for topic: {topic}")
        return f"""
        Get a paper from {archive} about {topic} and return these fields about the paper:

        1. What problem is the paper addressing?
        2. What is the proposed solution or method?
        3. What are the remaining challenges?
        4. What techniques are used, and what are they applied to?
        5. What domains could this work apply to?
        6. paper url

        Return the result as a JSON structured like this:

        {{
            "problem": "...",
            "solution": "...",
            "challenges": "...",
            "techniques": "...",
            "domains": "...",
            "url": "..."
        }}

        Only return the JSON object. Do not include any commentary, explanation, or additional formatting.
        """

    def run(self, archive: str, topic: str):
        query = self.build_query(archive, topic)
        logger.info(f"Sending query for topic: {topic}")
        try:
            response = self.client.query(query)
            logger.info("Query completed successfully.")
            return response
        except Exception as e:
            logger.error(f"Failed to query Perplexity: {e}")
            raise
