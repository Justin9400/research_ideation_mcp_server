import os
from fastmcp import FastMCP
from dotenv import load_dotenv
from archive_classifier import ArchiveClassifier
from mcp_middleware import MCPMiddleware
from openrouter_metadata_workflow_v2 import OpenRouterMetadataWorkflowV2
from perplexity_metadata_workflow import PerplexityMetadataWorkflow
from openrouter_metadata_workflow import OpenRouterMetadataWorkflow

load_dotenv()
API_KEY = os.getenv("MCP_API_KEY")

mcp = FastMCP("MCP Demo")

# workflow_perplexity = PerplexityMetadataWorkflow()
workflow_openrouter = OpenRouterMetadataWorkflow()
workflow_openrouter_v2 = OpenRouterMetadataWorkflowV2()
archive_classifier = ArchiveClassifier()

# @mcp.tool
# async def get_metadata(search_query: str):
#     ''' Retrieve structured metadata about a research topic from a specific archive using Perplexity '''

#     return workflow_perplexity.run(search_query)

@mcp.tool
async def get_metadata(search_query: str):
    ''' Retrieve structured metadata about a research topic from a specific archive using OpenRouter '''

    return workflow_openrouter.run(search_query)

@mcp.tool
async def get_metadata_v2(search_query: str):
    ''' Retrieve structured metadata about a research topic from a specific archive using OpenRouter '''

    return workflow_openrouter_v2.run(search_query)

@mcp.tool
async def get_metadata_v2(search_query: str):
    ''' Retrieve structured metadata about a research topic from a specific archive using OpenRouter '''

    return archive_classifier.run(search_query)

# if __name__ == "__main__":
#     mcp.run(
#         transport="http",
#         port=3333,
#         path="/nmj-mcp",
#         log_level="debug",
#         middleware=[
#             (MCPMiddleware, {}, {"api_key": API_KEY})
#         ]
#     )

app = mcp.http_app(
    path="/nmj-mcp",
    middleware=[
        (MCPMiddleware, {}, {"api_key": API_KEY})
    ]
)
