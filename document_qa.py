
import os
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI

import chainlit as cl
from chainlit.types import AskFileResponse


# chunks: max length of text that can be processed in a single input
# chunk_overlap: includes portion of previous chunk into the current one, to provide context between adjacent chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
embeddings = OpenAIEmbeddings()

welcome_message = """Welcome to the Chainlit PDF QA demo! To get started:
1. Upload a PDF or text file
2. Ask a question about the file
"""

# loading file data, splitting into chunks and chunk labeling 
def process_file(file: AskFileResponse):
    import tempfile

    # text file
    if file.type == "text/plain":
        Loader = TextLoader
    # PDF
    elif file.type == "application/pdf":
        Loader = PyPDFLoader
    
    with tempfile.NamedTemporaryFile() as tempfile:
        tempfile.write(file.content)
        loader = Loader(tempfile.name)
        documents = loader.load()
        # getting chunks
        docs = text_splitter.split_documents(documents)
        # labeling them as sources
        for i, doc in enumerate(docs):
            doc.metadata['source'] = f'source_{i}'
        return docs
    
def get_docsearch(file: AskFileResponse):
    docs = process_file(file)

    cl.user_session.set('docs', docs)
    
    # organizes documents into the vector space: used for document search and retrieval
    docsearch = Chroma.from_documents(
        docs,
        embeddings
    )
    return docsearch

@cl.on_chat_start
async def start():
    await cl.Message(content = "You can now chat with your PDFs").send()
    files = None

    # retrieving file
    while files is None:
        files = await cl.AskFileMessage(
            content = welcome_message,
            accept = ['text/plain', 'application/pdf'],
            max_size_mb = 20,
            timeout = 180,
        ).send()
     # only file submitted   
    file = files[0]

    msg = cl.Message(content = f'Processing {file.name} ...')
    await msg.send()

    docsearch = await cl.make_async(get_docsearch)(file)

    # using docsearch as retriever: performs ranking and retrieve relevant documents
    # with QA chain using GPT: not just keyword-matching but also contextually relevant
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature = 0, streaming = True),
        chain_type='stuff',
        retriever = docsearch.as_retriever(max_tokens_limit=4097)
    )

    msg.content = f"{file.name} processed. You can now ask questions!"
    await msg.update()

    cl.user_session.set('chain', chain)

@cl.on_message
async def main(message):
    chain = cl.user_session.get('chain')
    # allows streaming generation
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer = True,
        answer_prefix_tokens = ['FINAL', 'ANSWER']
    )
    cb.answer_reached = True
    # retrieving answer 
    res = await chain.acall(message, callbacks = [cb])

    answer = res['answer']
    sources = res['sources'].strip()
    source_elements = []

    # get documents
    docs = cl.user_session.get('docs')
    metadatas = [doc.metadata for doc in docs]
    all_sources = [m['source'] for m in metadatas]

    if sources:
        found_sources = []

        # basically, turning documents into Chainlit text elements
        for source in sources.split(','):
            
            print(source)
            print(source.strip())
            source_name = source.strip().replace('.', '') # ???

            # get index of source
            try:
                index = all_sources.index(source_name)
            except ValueError:
                continue
            text = docs[index].page_content
            found_sources.append(source_name)

            # create text element referenced in message, as clickable elements
            source_elements.append(cl.Text(content = text, name = source_name))
        
        if found_sources:
            answer += f"\nSources: {', '.join(found_sources)}"
        else:
            answer += '\nNo sources found'



    # adding source_elements at end of the answer   
    if cb.has_streamed_final_answer:
        cb.final_stream.elements = source_elements
        await cb.final_stream.update()
    else:
        await cl.Message(content=answer, elements = source_elements).send()




