# imports
import warnings
import json
import random
warnings.filterwarnings('ignore')
from openai import OpenAI
from litellm import completion as LLMBackend, completion_cost, token_counter
from litellm import embedding
import os
import time
import re
import numpy as np


# constants/args
API_TOKEN = "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"
GPT_4 = 'openai/gpt-4-1106-preview'
GPT_3 = 'openai/gpt-3.5-turbo-1106'
GPT_3_1 = GPT_3
GPT_3_2 = 'openai/gpt-3.5-turbo-0301'
INSTRUCT = 'openai/gpt-3.5-turbo-instruct'
ZEPHR = "replicate/nateraw/zephyr-7b-beta:b79f33de5c6c4e34087d44eaea4a9d98ce5d3f3a09522f7328eea0685003a931"
OPENCHAT = 'replicate/nateraw/openchat_3.5-awq:ded16ea9889fe7c536c105b0b5f5142db79e4e38f92db2703e0ff59da1c10999'
LLAMA_JSON = "andreasjansson/llama-2-13b-chat-gguf:60ec5dda9ff9ee0b6f786c9d1157842e6ab3cc931139ad98fe99e08a35c5d4d4"
STARLING = 'replicate/tomasmcm/starling-lm-7b-alpha:1cee13652378fac04fe10dedd4c15d3024a0958c3e52f97a1aa7c4d05b99ef99'
# init 
client = OpenAI(api_key=API_TOKEN)
os.environ['REPLICATE_API_TOKEN'] = 'r8_Wcldf1xWHXw03iwcCfrkRm6YByeE1DN0eJhr5'
os.environ["OPENAI_API_KEY"] = API_TOKEN


