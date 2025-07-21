import os
from fastmcp import FastMCP
from dotenv import load_dotenv
from mcp_middleware import MCPMiddleware
from extract_arxiv_meta_data import ArxivMetadataWorkflow
from extract_pubmed_meta_data import PubMedMetadataWorkflow
from extract_biorxiv_meta_data import BioRxivMetadataWorkflow
from extract_chemrxiv_meta_data import ChemRxivMetadataWorkflow

load_dotenv()
API_KEY = os.getenv("MCP_API_KEY")

mcp = FastMCP("MCP Demo")

pubmed = PubMedMetadataWorkflow(email="your@email.com")
arxiv = ArxivMetadataWorkflow()
biorxiv = BioRxivMetadataWorkflow()
chemrxiv = ChemRxivMetadataWorkflow()

@mcp.tool
def search_pubmed(search_query: str, max_retrievals: int):
    ''' Retrieve n number of papers from PubMed '''

    return pubmed.run(search_query, max_retrievals)

@mcp.tool
def search_arxiv(search_query: str, max_retrievals: int):
    ''' Retrieve n number of papers from arXiv '''

    return arxiv.run(search_query, max_retrievals)

@mcp.tool
def search_biorxiv(search_query: str, max_retrievals: int):
    ''' Retrieve n number of papers from bioRxiv '''

    return biorxiv.run(search_query, max_retrievals)

@mcp.tool
def search_chemrxiv(search_query: str, max_retrievals: int):
    ''' Retrieve n number of papers from chemRxiv '''

    return chemrxiv.run(search_query, max_retrievals)

if __name__ == "__main__":
    mcp.run(
        transport="http",
        # host="127.0.0.1",
        port=3333,
        path="/nmj-mcp",
        log_level="debug",
        middleware=[
            (MCPMiddleware, {}, {"api_key": API_KEY})
        ]
    )