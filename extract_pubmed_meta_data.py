import logging
from Bio import Entrez
from paper import Paper
from typing import List
from langgraph.graph import StateGraph
from graph_state import GraphState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("KGBuilder")

class PubMedMetadataWorkflow:
    def __init__(self, email: str):
        Entrez.email = email

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

            logger.info(f"Searching PubMed for: '{search_query}' (retrieving {max_retrievals} papers)")

            with Entrez.esearch(db="pubmed", term=search_query, retmax=max_retrievals) as handle:
                search_results = Entrez.read(handle)

            pmid_list = search_results.get("IdList", [])

            if not pmid_list:
                logger.warning("No papers found for query: {search_query}", e)
                raise ValueError("No results found for query.")

            with Entrez.efetch(db="pubmed", id=",".join(pmid_list), rettype="medline", retmode="xml") as handle:
                fetch_results = Entrez.read(handle)

            papers: List[dict] = []

            for article_record in fetch_results["PubmedArticle"]:
                article = article_record["MedlineCitation"]["Article"]

                title = article.get("ArticleTitle", "")
                abstract_text = article.get("Abstract", {}).get("AbstractText", [""])
                summary = abstract_text[0] if isinstance(abstract_text, list) else abstract_text

                authors = [
                    f"{a.get('ForeName', '')} {a.get('LastName', '')}".strip()
                    for a in article.get("AuthorList", [])
                    if "ForeName" in a and "LastName" in a
                ]

                doi = ""
                for article_id in article_record.get("PubmedData", {}).get("ArticleIdList", []):
                    if article_id.attributes.get("IdType") == "doi":
                        doi = str(article_id)
                        break

                if not doi:
                    doi = str(article_record["MedlineCitation"]["PMID"])

                papers.append(Paper(
                    doi=doi,
                    title=title,
                    authors=authors,
                    summary=summary
                ))

            state["papers"] = papers
            return state

        except Exception as e:
            logger.warning("Failed to retrieve papers (%s).", e)
            return {"error": str(e), **state}



    def _build_graph(self):
        logger.info("building PubMed graph")

        workflow = StateGraph(GraphState)
        workflow.add_node("FetchPubMedMetadata", self._fetch_meta_data)
        workflow.set_entry_point("FetchPubMedMetadata")
        workflow.set_finish_point("FetchPubMedMetadata")
        final_flow = workflow.compile()

        logger.info("PubMed graph built")

        return final_flow
