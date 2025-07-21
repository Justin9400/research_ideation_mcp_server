import logging
import requests
from paper import Paper
from typing import List
from graph_state import GraphState
from langgraph.graph import StateGraph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("KGBuilder")

class BioRxivMetadataWorkflow:
    def __init__(self):
        pass

    def run(self, search_query: str, max_retrievals) -> dict:
        initial_state: GraphState = {
            "search_query": search_query,
            "max_retrievals": max_retrievals,
            "papers": []
        }
        app = self._build_graph()
        final_state = app.invoke(initial_state)
        return final_state

    def _fetch_meta_data(self, state: GraphState) -> GraphState:
        try:
            query = state["search_query"]
            # query = "bioRxiv"
            limit = state["max_retrievals"]
            logger.info(f"Searching BioRxiv for: '{query}' (retrieving {limit} papers)")
# https://api.biorxiv.org/details/biorxiv/2025-03-21/2025-03-28?category=cell_biology
            # url = f"https://api.biorxiv.org/pub/biorxiv/category={query}/0/{limit}"
            url = "https://api.biorxiv.org/details/biorxiv/2025-03-21/2025-03-28?category={query}"
            # url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
            # url = f"https://api.biorxiv.org/details/biorxiv/{query}/0/{limit}"
#     query = "bioRxiv"  # Specify bioRxiv as the source            


            response = requests.get(url)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}")

            data = response.json()

            collection = data.get("collection", [])
            if not collection:
                raise Exception("No results returned from BioRxiv")

            papers: List[Paper] = []
            for entry in collection:
                doi = entry.get("doi", "N/A")
                title = entry.get("title", "")
                abstract = entry.get("abstract", "")
                authors = entry.get("authors", "").split("; ")

                papers.append(Paper(
                    doi=doi,
                    title=title,
                    authors=authors,
                    summary=abstract
                ))

            state["papers"] = papers
            return state

        except Exception as e:
            logger.warning(f"Error fetching BioRxiv metadata: {e}", exc_info=True)
            return {"error": str(e), **state}

    def _build_graph(self):
        logger.info("building BioRxiv graph")

        workflow = StateGraph(GraphState)
        workflow.add_node("FetchBioRxivMetadata", self._fetch_meta_data)
        workflow.set_entry_point("FetchBioRxivMetadata")
        workflow.set_finish_point("FetchBioRxivMetadata")

        logger.info("building BioRxiv graph")

        return workflow.compile()
