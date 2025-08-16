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


class OpenRouterMetadataWorkflow:
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

    def build_query(self, topic: str) -> str:
        logger.debug(f"Building query for topic: {topic}")
        return f"""
            You are a scientific research assistant that performs two tasks.

            ### TASK 1: Classify the topic of {topic} to the appropriate academic archive

            Given a research topic or subject, classify which of the following archives it is most relevant to:

            - arXiv: Physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering and systems science, and economics
            - PubMed: Biomedicine and health, with related fields in the life sciences, behavioral sciences, chemical sciences, and bioengineering.
            - bioRxiv: Biochemistry, Bioinformatics, Biophysics, Cancer Biology, Cell Biology, Developmental Biology, Ecology, Evolutionary Biology, Genetics, Genomics, Immunology, Microbiology, Molecular Biology, Neuroscience, Paleontology, Pathology, Pharmacology and Toxicology, Physiology, Plant Biology, Scientific Communication and Education, Synthetic Biology, Systems Biology, and Zoology.
            - ChemRxiv: Agricultural and Food Chemistry, Analytical Chemistry, Biological and Mecidinal Chemistry, Catalysis, Chemical Education, Chemical Engineering and Industrial Chemistry, Earth Chemistry, Space Chemistry, Environmental Chemistry, Energy, Inorganic Chemistry, Materials Chemistry, Nanoscience and Nanotechnology, Organic Chemistry, Organometallic Chemistry, Physical Chemistry, Polymer Chemistry, Theoretical and Computational Chemistry.

            Respond with the single best matching archive based on the topic.

            ### TASK 2: Get a paper from the selected archive about the topic and extract structured information.

            Given the selected archive and the topic, retrieve a relevant paper and extract the following fields:

            1. What is the title of the paper?
            2. What are the references of the paper?
            3. What problem is the paper addressing? Break this down into a list of topics or phrases.
            4. What is the proposed solution or method? Break this down into a list of solutions or methods.
            5. What are the remaining challenges? Break this down into a list of challenges.
            6. What techniques are used, and what are they applied to? Break this down into a list of techniques and things that they are applied to.
            7. What domains could this work apply to? Break this down into a list of work domains that this could apply to.
            8. The paper URL.

            Return the result as a **JSON object only**, with the following structure:

            {{
                "title": "...",
                "references": [...],
                "problem": [...],
                "solution": [...],
                "challenges": [...],
                "techniques": [...],
                "domains": [...],
                "url": "..."
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
