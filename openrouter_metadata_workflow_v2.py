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


class OpenRouterMetadataWorkflowV2:
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

        return f"""You are a scientific research assistant that performs two tasks.

            ### TASK 1: Classify the Topic
            Given the research topic: {topic}, classify it into one of the following academic archives:

            - arXiv: Physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering and systems science, and economics
            - PubMed: Biomedicine and health, with related fields in the life sciences, behavioral sciences, chemical sciences, and bioengineering.
            - bioRxiv: Biochemistry, Bioinformatics, Biophysics, Cancer Biology, Cell Biology, Developmental Biology, Ecology, Evolutionary Biology, Genetics, Genomics, Immunology, Microbiology, Molecular Biology, Neuroscience, Paleontology, Pathology, Pharmacology and Toxicology, Physiology, Plant Biology, Scientific Communication and Education, Synthetic Biology, Systems Biology, and Zoology.
            - ChemRxiv: Agricultural and Food Chemistry, Analytical Chemistry, Biological and Mecidinal Chemistry, Catalysis, Chemical Education, Chemical Engineering and Industrial Chemistry, Earth Chemistry, Space Chemistry, Environmental Chemistry, Energy, Inorganic Chemistry, Materials Chemistry, Nanoscience and Nanotechnology, Organic Chemistry, Organometallic Chemistry, Physical Chemistry, Polymer Chemistry, Theoretical and Computational Chemistry.

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
