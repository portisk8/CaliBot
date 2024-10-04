import os
from typing import List
import json
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders.base import BaseLoader
from langchain.docstore.document import Document

class RAGTrainer:
    def __init__(self, api_key: str, embedding_model: str = "text-embedding-ada-002", have_to_train: bool = True):
        # el constructor por defecto toma un embedding, pero luego lo sobreescribe tomando
        # el string existente en el appsettings
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.vectorstore = None
        if(not have_to_train):
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            self.vectorstore = Chroma(persist_directory=f"ChromaDB", embedding_function=embeddings)

    @staticmethod
    def load_text_with_error_handling(file_path):
        encodings = ['utf-8', 'latin-1', 'ascii']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        print(f"Could not decode file {file_path} with any known encoding.")
        return ""

    @staticmethod
    def load_json_with_error_handling(file_path):
        encodings = ['utf-8', 'latin-1', 'ascii']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return json.load(file)
            except UnicodeDecodeError:
                continue
        print(f"Could not decode file {file_path} with any known encoding.")
        return ""

    class CustomLoader(BaseLoader):
        def __init__(self, file_path: str):
            self.file_path = file_path

        def load(self) -> List[Document]:
            if self.file_path.endswith('.json'):
                return self.load_json()
            else:  # Assume it's a text or markdown file
                return self.load_text()

        def load_text(self) -> List[Document]:
            text = RAGTrainer.load_text_with_error_handling(self.file_path)
            metadata = {"source": self.file_path}
            return [Document(page_content=text, metadata=metadata)]

        def load_json(self) -> List[Document]:
            data = RAGTrainer.load_json_with_error_handling(self.file_path)
            documents = []
            for item in data:
                if isinstance(item, dict) and 'content' in item:
                    content = item['content']
                    metadata = {k: v for k, v in item.items() if k != 'content'}
                    metadata['source'] = self.file_path
                    documents.append(Document(page_content=content, metadata=metadata))
            return documents

    '''
    Este método es el que realiza la carga de TODOS los documentos de texto existentes 
    a la base de datos de Chroma. En nuestro caso, en el directorio training_data,
    volcamos un documento de QuestionAnswer.txt conteniendo las FAQ de la App
    Esto permite dinamismo en el sistema de diáologo
    '''
    def train(self, knowledge_base_path: str):
        # Load documents
        loader = DirectoryLoader(knowledge_base_path, glob=["**/*.md", "**/*.json","**/*.txt"], loader_cls=self.CustomLoader)
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

        # Create embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)

        # Create vector database
        self.vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=f"ChromaDB")

    '''
    Este método permite recuperar los vectores (embeddings) que serán utilizados al momento de "aumentar"
    la capacidad del LLM, con datos propios
    Los datos propios son los que se encuentran en la carpeta training_data (QuestionAnswer.txt)
    '''
    def get_retriever(self, k: int = 3):
        if self.vectorstore is None:
            raise ValueError("You must train the model before getting a retriever.")
        return self.vectorstore.as_retriever(search_kwargs={"k": k})