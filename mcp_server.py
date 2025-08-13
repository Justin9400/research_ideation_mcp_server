import os
from fastmcp import FastMCP
from dotenv import load_dotenv
from mcp_middleware import MCPMiddleware
from perplexity_metadata_workflow import PerplexityMetadataWorkflow

load_dotenv()
API_KEY = os.getenv("MCP_API_KEY")

mcp = FastMCP("MCP Demo")

# workflow_perplexity = PerplexityMetadataWorkflow()
workflow_openrouter = OpenRouterMetadataWorkflow()

# @mcp.tool
# async def get_metadata(search_query: str):
#     ''' Retrieve structured metadata about a research topic from a specific archive using Perplexity '''

#     return workflow_perplexity.run(search_query)

@mcp.tool
async def get_metadata(search_query: str):
    ''' Retrieve structured metadata about a research topic from a specific archive using OpenRouter '''

    return workflow_openrouter.run(search_query)

    return workflow.run(search_query)

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
