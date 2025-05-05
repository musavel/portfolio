import os
import sys

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config

from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

class KoSimCSEEmbedding:
    def __init__(self, model_name="BM-K/KoSimCSE-roberta"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return (token_embeddings * input_mask_expanded).sum(1) / input_mask_expanded.sum(1)

    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        encoded = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            model_output = self.model(**encoded)
        embedding = self._mean_pooling(model_output, encoded['attention_mask'])
        return embedding[0].cpu().numpy().tolist()

def set_llm(temperature):
    llm = ChatOpenAI(
        model=Config.OPENAI_MODEL
        , temperature=temperature
        , api_key=Config.OPENAI_API_KEY
    )
    
    return llm

def set_embedding(embed_type='OpenAI'):
    if embed_type == 'OpenAI':
        embedding = OpenAIEmbeddings(
            model=Config.EMBED_MODEL
            , api_key=Config.OPENAI_API_KEY
        )
    elif embed_type == 'KoSimCSE':
        embedding = KoSimCSEEmbedding(
            model_name="BM-K/KoSimCSE-roberta"
        )
    
    return embedding