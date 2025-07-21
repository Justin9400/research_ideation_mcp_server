import arxiv
import logging
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

class ArxivMetadataWorkflow:
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
            limit = state["max_retrievals"]
            logger.info(f"Searching arXiv for: '{query}' (retrieving {limit} papers)")

            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=arxiv.SortCriterion.Relevance
            )
            client = arxiv.Client()

            papers: List[Paper] = []
            for result in client.results(search):
                paper = Paper(
                    doi=result.entry_id,
                    title=result.title,
                    authors=[a.name for a in result.authors],
                    summary=result.summary
                )
                papers.append(paper)

            state["papers"] = papers
            return state

        except Exception as e:
            logger.warning(f"Error fetching arXiv metadata: {e}", exc_info=True)
            return {"error": str(e), **state}

    def _build_graph(self):
        logger.info("building arXiv graph")

        workflow = StateGraph(GraphState)
        workflow.add_node("FetchArxivMetadata", self._fetch_meta_data)
        workflow.set_entry_point("FetchArxivMetadata")
        workflow.set_finish_point("FetchArxivMetadata")

        logger.info("building arXiv graph")

        return workflow.compile()
