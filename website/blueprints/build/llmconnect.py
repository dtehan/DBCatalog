import os, sys
from dotenv import load_dotenv, find_dotenv
from crews.writer_crew.azure_writer_crew import AzureWriterCrew
from crews.writer_crew.bedrock_writer_crew import BedrockWriterCrew
from flask import session
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [("human", "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three to five sentences maximum and keep the answer concise. Question: {question} Context: {context} Answer:"),]
    )

# State for the chat application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


def load_env():
    _ = load_dotenv(find_dotenv('DBCatalog.env'))


# LLMConnect class connects to a LLM as defined in the DBCatalog.env file
class LLMConnect():
    def __init__(self):
        load_env()

    # Connect instantiates the model
    def connect(self):
        # get the llm object
        try:
            session['crew_type'] = os.getenv("crew_type")
            if os.getenv("crew_type") == "Azure-GPT":
                self.llmCrew = AzureWriterCrew()
                print("using Azure LLM")
            elif "Bedrock" in os.getenv("crew_type"):
                self.llmCrew = BedrockWriterCrew()
                print("using Bedrock LLM")
            else:
                print("Could not identify LLM")
        except:    # Specify in standard error any other error encountered
            print("Script Failure :", sys.exc_info()[0], file=sys.stderr)
            raise
            sys.exit()

    # get_table_description takes a "create table" string and returns a business definition of the table from the LLM
    def get_table_description(self, inputString):
        try:
            input = {'table_definition': inputString}
            outputString = self.llmCrew.kickoff(inputs=input)
            return outputString
        except:    # Specify in standard error any other error encountered
            print("Script Failure :", sys.exc_info()[0], file=sys.stderr)
            raise
            sys.exit()

    def embed_connect(self):
        self.embed = AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("azure_embed_endpoint"),
            api_key=os.getenv("azure_api_key"),
            openai_api_version=os.getenv("azure_api_version"),
        )

    def chat_connect(self):
        self.chat = AzureChatOpenAI(
            azure_endpoint=os.getenv("azure_endpoint"),
            api_key=os.getenv("azure_api_key"),
            openai_api_version=os.getenv("azure_api_version"),
        )
        
    def vdb_create(self):
        self.vdb = Chroma(embedding_function=self.embed, persist_directory='chromadb/', collection_name="table")

    def vdb_add(self, doc, id):
        self.vdb.add_documents(documents=[doc], ids=[id])

    def vdb_delete(self, id):
        self.vdb.delete(ids=[id])
    
    # Define application steps
    def vdb_retrieve(self, state: State):
        retrieved_docs = self.vdb.similarity_search(state["question"], k=5)
        return {"context": retrieved_docs}


    def vdb_generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = self.chat.invoke(messages)
        return {"answer": response.content}

    def vdb_chat_graph(self):
        graph_builder = StateGraph(State).add_sequence([("retreive", self.vdb_retrieve),("generate", self.vdb_generate)])
        graph_builder.add_edge(START, "retreive")
        self.graph = graph_builder.compile()

    def vdb_chat(self, question):
        response = self.graph.invoke({"question": question})
        return(response["answer"])