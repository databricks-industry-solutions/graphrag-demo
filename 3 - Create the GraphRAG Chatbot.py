# Databricks notebook source
# MAGIC %md
# MAGIC # Create the GraphRAG chatbot with Langchain and Neo4j
# MAGIC

# COMMAND ----------

# MAGIC %pip install -q python-dotenv neo4j langchain-openai databricks-agents databricks_langchain mlflow mlflow-skinny langchain==0.2.1 langchain_core==0.2.5 langchain_community==0.2.4

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# COMMAND ----------

# Define the path to the .env file located in the "code" directory
dot_env_path = Path("/model/code/.env")

# Initialize a variable to track if the .env file is loaded
is_env_loaded = None

# Check if the .env file exists at the specified path
if dot_env_path.exists():
    # Print a message indicating the .env file was found
    print(".env file found in code")
    # Load environment variables from the specified .env file (in case it is invoked from a serving endpoint)
    is_env_loaded = load_dotenv(dotenv_path=dot_env_path)
else:
    # Print a message indicating the .env file was not found
    print(".env file not found in code")
    # Load environment variables from a default .env file if the specified one does not exist
    is_env_loaded = load_dotenv()

# Raise an exception if the environment variables were not loaded properly
if not is_env_loaded:
    raise Exception(f"Environment variables not loaded properly from .env file")

# COMMAND ----------

neo4j_url = os.getenv('NEO4J_URL')
neo4j_username = os.getenv('NEO4J_USER')
neo4j_password = os.getenv('NEO4J_PASSWORD')

# COMMAND ----------

from langchain_community.chat_models import ChatDatabricks
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
from langchain_core.runnables import RunnableLambda
import mlflow

# COMMAND ----------

# MAGIC %md
# MAGIC ## The importance of MLflow
# MAGIC
# MAGIC MLflow plays a key role in tracking and debugging the GraphCypherQAChain workflow. It lets you monitor model versioning, performance metrics, and artifacts, making deployment seamless and transparent. With MLflow, you can easily trace and optimize the outputs of the LLMs within its interface.
# MAGIC
# MAGIC

# COMMAND ----------

mlflow.langchain.autolog()

# COMMAND ----------

graph = Neo4jGraph(
    url=neo4j_url,
    username=neo4j_username,
    password=neo4j_password
)

# COMMAND ----------

# MAGIC %md
# MAGIC # Define the LLMs
# MAGIC
# MAGIC We are speaking prular as we use two different LLMs: 
# MAGIC -  the one stored in the variable `qa_llm`, is for managing the Q&A part
# MAGIC - the one stored in the variable `cypher_llm` is for managing the Text-2-Cypher conversion
# MAGIC
# MAGIC Each LLM has its own prompt as they're serving for different purposes.
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define the Q&A model

# COMMAND ----------

qa_llm = ChatDatabricks(
    endpoint="databricks-meta-llama-3-70b-instruct",
    temperature=0.1
)
qa_prompt = PromptTemplate(
    input_variables=["context", "question"], template=os.getenv('QA_GENERATION_TEMPLATE')
)
print(qa_prompt)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define the Text-2-Cypher model

# COMMAND ----------

# MAGIC %md
# MAGIC ### How to provision your Text-2-Cypher model
# MAGIC
# MAGIC Before moving forward, you can deploy your own Text-2-Cypher model by executing [this notebook]($./3.1 - Provisioned Throughput text2cypher serving example)

# COMMAND ----------

'''
Now you can choose to use the `text2cypher-demo-16bit` model deployed in the notebook linked above or use whatever other LLM you want, as for instance in the commented code for using gpt-4.
'''
# cypher_llm = ChatDatabricks(
#     endpoint="text2cypher-demo-16bit"
# )
cypher_llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv('OPEN_AI_API_KEY'),
    temperature=0.1
)
cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"], template=os.getenv('CYPHER_GENERATION_TEMPLATE')
)
print(cypher_prompt)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create and Test GraphRAG Chain
# MAGIC Now that we have defined our pretrained LLM and fine-tuned text2cypher model, and our data is loaded into the Neo4j graph database, we can then work on defining our agent. Details can be found in notebook.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Naive Chain
# MAGIC The Naive Chain approach involves using a pretrain LLM for both Cypher query generation and answer summarization, without the aid of advanced prompts or configurations. In this setup, GPT-4.0 is utilized as the primary model, where it takes in a user query, interprets it, generates the Cypher query, executes it against the Neo4j database, and finally summarizes the results. While this approach is straightforward, it may not fully leverage the flexibility and performance offered by using separate LLMs or more detailed prompts.
# MAGIC
# MAGIC An example code and results to use GPT-4.0 for this naive chain would look as follows:

# COMMAND ----------

# Create a GraphCypherQAChain instance using a language model from Databricks and the Neo4j graph
chain = GraphCypherQAChain.from_llm(
    # Pass the language model for the Q&A part
    qa_llm=qa_llm,
    # Use the predefined Cypher generation prompt template for the Q&A part
    qa_prompt=qa_prompt,
    # Pass the Neo4j graph instance
    graph=graph,
    # Enable verbose mode for detailed logging
    verbose=True,
    # Return intermediate steps for debugging
    return_intermediate_steps=True,
    # Pass the language model for the Text2Cypher part
    cypher_llm=cypher_llm,
    # Use the predefined Cypher generation prompt template for the Text2Cypher part
    cypher_prompt=cypher_prompt,
    # Allow potentially dangerous requests
    allow_dangerous_requests=True,
    # Validate the generated Cypher queries
    validate_cypher=False
) | RunnableLambda(lambda x: x["result"]) # The RunnableLambda step is used for properly extracting the result

# COMMAND ----------

# Log the GraphCypherQAChain instance as an MLflow model
mlflow.models.set_model(model=chain)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Log the chain
# MAGIC
# MAGIC Once the GraphRAG chain is logged, you can use chain.invoke() to pass a natural language query into the `GraphCypherQAChain`. The output includes the Cypher query and summarized response, enabling you to identify issues like query inaccuracies or misinterpretations. Testing the GraphRAG system in Databricks notebooks with MLflow tracing helps iteratively improve accuracy and reliability, ensuring it meets complex use cases like cybersecurity analysis or large-scale graph data retrieval.

# COMMAND ----------

# if it's not ran from the Databricks model serving endpoint please run this for debug
if not dot_env_path.exists():
  response = chain.invoke("Can you show potiential attack paths in our network to high value targets? Return the first five results")
