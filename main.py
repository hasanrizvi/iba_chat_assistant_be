import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

store = {}

class ChatBot():
  load_dotenv()

  text_loader_kwargs={'encoding': 'UTF-8'}
  loader = DirectoryLoader("./scraped_data/", glob="./*.txt", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
  documents = loader.load()

  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
  docs = text_splitter.split_documents(documents)

  persist_directory = 'faiss_db'
  repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

  embedding = HuggingFaceEmbeddings(
    show_progress=True
  )

  try:
    if os.path.exists(persist_directory):
      vectordb = FAISS.load_local(
        index_name="faiss_index",
        embeddings=embedding,
        folder_path=persist_directory,
        allow_dangerous_deserialization=True
      )
    else:
      # vector
      vectordb = FAISS.from_documents(docs, embedding)
      vectordb.save_local(
        folder_path=persist_directory,
        index_name="faiss_index"
      )

  except Exception as ex:
    print(f'Error: {ex}')

  retriever = vectordb.as_retriever()

  llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature=0.5,
    huggingfacehub_api_token=os.getenv('HUGGINGFACE_ACCESS_TOKEN')
  )

  template = """
  You are a virtual assistant made for answering questions related to Institute of Business Administration (IBA). \
  The students of this university will ask you some questions about the university. \
  Use the following pieces of retrieved context to answer the question. \
  If you don't know the answer, just say that you don't know. You don't need to mention that it is not in your context. \
  Provide answer with complete details in a proper formatted manner. \
  You don't need to give reference of the file you found your answer in. \

  Context: {context}
  Question: {input}
  Answer:
  """

  prompt = ChatPromptTemplate.from_template(template)
  document_chain = create_stuff_documents_chain(llm, prompt)
  retrieval_chain = create_retrieval_chain(retriever, document_chain)

app = Flask(__name__)
CORS(app)
lock = threading.Lock()

bot = ChatBot()

# GET routes
@app.route('/', methods=['GET'])
def get_data():
  return jsonify({'message': 'Server is running...'})

@app.route('/greeting-message', methods=['GET'])
def get_greeting_message():
  return jsonify({'message': """Welcome to Institute of Business Administration Chat Assistance

Hello there! Whether you're a new student eager to explore campus life or a returning student seeking guidance, you've come to the right place! \
I'm here to assist you with any queries you may have about courses, admissions, campus facilities, or anything else related to your academic journey. \
Feel free to ask away, and let's embark on this exciting educational adventure together!"""
})

# POST routes
@app.route('/ask', methods=['POST'])
def add_data():
  lock.acquire()

  try:
    input = request.json
    result = bot.retrieval_chain.invoke({"input": input['input']})
    print(result)
    return jsonify({'message': result["answer"]})
  finally:
    lock.release()

if __name__ == '__main__':
  app.run(debug=True)