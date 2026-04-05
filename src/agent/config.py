import tiktoken

MAX_TOOL_CALLS = 8       # Maximum tool calls per agent run
MAX_ITERATIONS = 10      # Maximum agent loop iterations
BASE_TOKEN_THRESHOLD = 2000     # Initial token threshold for compression
TOKEN_GROWTH_FACTOR = 0.9       # Multiplier applied after each compression

def estimate_context_tokens(messages: list) -> int:
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
    except:
        encoding = tiktoken.get_encoding("cl100k_base")
    return sum(len(encoding.encode(str(msg.content))) for msg in messages if hasattr(msg, 'content') and msg.content)