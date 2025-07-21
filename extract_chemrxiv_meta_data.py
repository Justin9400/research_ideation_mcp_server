import logging
import chemrxiv
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

class ChemRxivMetadataWorkflow:
    def __init__(self):
        pass

    def run(self, search_query: str, max_retrievals: int) -> dict:
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
            search_query = state["search_query"]
            max_retrievals = state["max_retrievals"]
            logger.info(f"Searching ChemRxiv for: '{search_query}' (retrieving {max_retrievals} papers)")

            client = chemrxiv.Client()
            search = chemrxiv.Search(term=search_query, limit=max_retrievals)
            
            results = client.results(search)

            papers: List[dict] = []
            
            for result in results:
                doi = result.doi or "N/A"
                title = result.title or ""
                authors = [author.name for author in result.authors]
                summary = result.abstract or ""

                papers.append(Paper(
                    doi=doi,
                    title=title,
                    authors=authors,
                    summary=summary
                ))
            
            state["papers"] = papers
            return state

        except Exception as e:
            logger.warning(f"Error fetching ChemRxiv metadata: {e}", exc_info=True)
            return {"error": str(e), **state}

    def _build_graph(self):
        logger.info("building ChemRxiv graph")

        workflow = StateGraph(GraphState)
        workflow.add_node("FetchChemRxiv", self._fetch_meta_data)
        workflow.set_entry_point("FetchChemRxiv")
        workflow.set_finish_point("FetchChemRxiv")
        final_flow = workflow.compile()

        logger.info("ChemRxiv graph built")

        return final_flow
