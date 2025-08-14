import os
import logging
from dotenv import load_dotenv
from perplexipy import PerplexityClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("PerplexityMetadataWorkflow")

class PerplexityMetadataWorkflowV2:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            logger.error("PERPLEXITY_API_KEY not found in environment variables.")
            raise EnvironmentError("Missing Perplexity API key.")
        self.client = PerplexityClient(api_key)
        logger.info("Perplexity client initialized.")

    def build_query(self, topic: str) -> str:
        logger.debug(f"Building query for topic: {topic}")

        return f"""You are a scientific research assistant that performs two tasks.

            ### TASK 1: Classify the Topic
            Given the research topic: {topic}, classify it into one of the following academic archives:

            - arXiv: physics, mathematics, computer science, statistics, quantitative biology, etc.
            - PubMed: peer-reviewed biomedical and clinical research (e.g., medicine, health, pharmacology).
            - bioRxiv: life sciences and biology preprints (e.g., genomics, neuroscience, molecular biology).
            - ChemRxiv: chemistry preprints (e.g., organic, inorganic, physical, analytical chemistry).

            Respond with the single best matching archive name only.

            ### TASK 2: Retrieve and Extract Paper Information
            From the chosen archive, retrieve a relevant paper about {topic} and extract the following fields, based on the definitions below:

            1. Context – The status quo of related literature or reality that motivated this study (problem, research question, or gap not addressed by previous work).
            2. Key Idea – The main intellectual merit or novel idea/solution proposed in this study, compared to existing literature.
            3. Method – The specific research method used to test or validate the key idea (experimental setup, theoretical framework, or other validation methods).
            4. Outcome – The factual results and conclusions, including whether the hypothesis was supported.
            5. Projected Impact – The anticipated impact on the field, including possible future research directions.

            ### Output Format
            Return your final answer as a single JSON object in this format, with no extra text or commentary:

            {{
                "archive": "arXiv",
                "context": "...",
                "key_idea": "...",
                "method": "...",
                "outcome": "...",
                "projected_impact": "..."
            }}
            """


    def run(self, topic: str):
        query = self.build_query(topic)
        logger.info(f"Sending query for topic: {topic}")
        try:
            response = self.client.query(query)
            logger.info("Query completed successfully.")
            return response
        except Exception as e:
            logger.error(f"Failed to query Perplexity: {e}")
            raise
