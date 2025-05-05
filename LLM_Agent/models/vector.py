import os
import sys

from langchain_chroma.vectorstores import Chroma

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config

def set_vectorstore(collection_name, embedding):
    vectorstore = Chroma(
        collection_name=collection_name
        , embedding_function=embedding
        , persist_directory=Config.CHROMADB_PATH
    )
    
    return vectorstore