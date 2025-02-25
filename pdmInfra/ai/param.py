"""
This file contains the configuration parameters for the PDM Infrastructure, which includes the LLM API parameters.
"""

# =-=-=-=-=-=-=-=-=-=-=- LLM API Parameters =-=-=-=-=-=-=-=-=-=-=-=


openaiNormalLLMList = ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18', 'gpt-4o', 'gpt-4o-mini']
openaiReasoningLLMList = ["o1-2024-12-17", "o3-mini"]
openaiLLMList = openaiNormalLLMList + openaiReasoningLLMList
googleLLMList = []
# googleLLMList = ["gemini-1.5-flash-002", "gemini-1.5-pro-002"]
pplxLLMList = []
# pplxLLMList = ["sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro"]
mistralLLMList = ["mistral-large-latest", "mistral-small"]
anthropicLLMList = ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
metaLLMList = []
deepseekLLMList = []
huggingfaceLLMList = []

validLLMList = openaiLLMList + pplxLLMList + mistralLLMList + anthropicLLMList + metaLLMList + deepseekLLMList + huggingfaceLLMList


openaiURL = "https://api.openai.com/v1/chat/completions"
pplxURL = "https://api.perplexity.ai/chat/completions"
mistralURL = "https://api.mistral.ai/v1/chat/completions"
anthropicURL = "https://api.anthropic.com/v1/messages"
googleURL = ""



