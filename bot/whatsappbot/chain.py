from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.query_constructor.base import (StructuredQueryOutputParser, get_query_constructor_prompt)
from langchain_community.query_constructors.pinecone import PineconeTranslator
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from dotenv import load_dotenv
import os
from .PromptEng import get_template
from .examples import get_examples

load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

def create_chain(vectorStore):
    model=ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-70b-versatile")
    # model=ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4o-mini")
    chain = create_stuff_documents_chain(
        llm=model,
        prompt=get_template(),
    )


    # Define metadata field information
    metadata_field_info = [
        AttributeInfo(
            name="course",
            description='The course relevant to the document. You must pick one of "Programming", "3D Design" or "Other".',
            type="string",
        ),
        AttributeInfo(
            name="subject",
            description='The subject relevant to the document. One of "Programming", "Electronics", "3D Design", "Manufacturing" or "Other".',
            type="string",
        ),
    ]

    document_content_description = "Brief description of educational content"


    prompt = get_query_constructor_prompt(
        document_content_description,
        metadata_field_info,
        examples=get_examples(),
    )
    output_parser = StructuredQueryOutputParser.from_components()
    query_constructor = prompt | model | output_parser

    self_query_retriever = SelfQueryRetriever(
    query_constructor=query_constructor,
    vectorstore=vectorStore,
    structured_query_translator=PineconeTranslator(),
    )

    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("human", "Given the above conversation, generate a search query to look up in order to get information relevant to the " +
                "conversation from the knowledge base. Additionally we are filtering the database for the most relevant vectors before " +
                "doing the similarity search. Filtering criteria are course[one of 'Programming', '3D Design' or 'Other'], and subject[one " +
                "of 'Programming', 'Electronics', '3D Design', 'Manufacturing' or 'Other']. Your response must contain the search query and the " +
                "filtering criteria. Do not include anything else. Let's think step by step."),
    ])


    history_aware_retriever = create_history_aware_retriever(
        llm=model,
        retriever=self_query_retriever,
        prompt=retriever_prompt
    )

    retrieval_chain = create_retrieval_chain(
        history_aware_retriever,
        chain
    )

    return retrieval_chain