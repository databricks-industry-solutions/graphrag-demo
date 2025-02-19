# Databricks notebook source
# MAGIC %md
# MAGIC # Provisioned Throughput Text2Cypher serving example
# MAGIC
# MAGIC Pretrained LLMs power GraphRAG agents by handling Cypher query generation and natural language responses. They transform natural language into structured Cypher queries and interpret results into user-friendly answers. On Databricks, models like GPT-4.0o and Llama 3 can be integrated and served efficiently with [Mosaic AI Model Serving](https://docs.databricks.com/en/machine-learning/model-serving/index.html#mosaic-ai-model-serving), enabling scalable, reproducible deployments. Below are code snippets to set up these models, allowing easy experimentation and comparison to find the best solution for your application.
# MAGIC
# MAGIC
# MAGIC Provisioned Throughput provides optimized inference for Foundation Models with performance guarantees for production workloads. Currently, Databricks supports optimizations for Llama3.x, Mosaic MPT, and Mistral class of models.
# MAGIC
# MAGIC This example walks through:
# MAGIC
# MAGIC 1. Downloading the model from Hugging Face `transformers`
# MAGIC 2. Logging the model in a provisioned throughput supported format into the Databricks Unity Catalog or Workspace Registry
# MAGIC 3. Enabling provisioned throughput on the model

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prerequisites
# MAGIC - Attach a cluster with sufficient memory to the notebook
# MAGIC - Make sure to have MLflow version 2.11 or later installed
# MAGIC - Make sure to enable **Models in UC**, especially when working with models larger than 7B in size
# MAGIC

# COMMAND ----------

# MAGIC %md 
# MAGIC ## Step 1: Log the model for optimized LLM serving

# COMMAND ----------

# Update/Install required dependencies
!pip install -U mlflow transformers accelerate
!pip install torchvision

# COMMAND ----------

# MAGIC %%capture
# MAGIC # Installs Unsloth, Xformers (Flash Attention) and all other packages!
# MAGIC !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
# MAGIC !pip install --no-deps "xformers<0.0.26" trl peft accelerate bitsandbytes

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Text2Cypher model from HuggingFace
# MAGIC General purpose LLMs often prove limited in certain specialty, so using a fine-tuned model for translating text to cypher leads to much better performance in practice. In this case, we’ll deploy a lightweight text2cypher model, fine-tuned based on the Llama 3 8B model. It is open-sourced on Hugging Face.
# MAGIC
# MAGIC In our code demo, the deployment of the text2cypher model is managed in the notebook “3.1 - Provisioned Throughput text2cypher serving example”, which:
# MAGIC
# MAGIC * Downloads the model from Hugging Face
# MAGIC * Logs the model in Unity Catalog
# MAGIC * Deploys a provisioned throughput model serving endpoint
# MAGIC
# MAGIC Once your endpoint is ready, you can query it by making an API request or testing it directly in the UI for seamless interaction. Deployment time may vary depending on the model's size and complexity. For instance, deploying the 8B text2cypher model was remarkably efficient, taking only 1 minute to complete. Further examples can be found [here](https://docs.databricks.com/en/machine-learning/foundation-model-apis/deploy-prov-throughput-foundation-model-apis.html#notebook-examples). 
# MAGIC

# COMMAND ----------

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "tomasonjo/text2cypher-demo-16bit", 
    torch_dtype=torch.bfloat16,
)
tokenizer = AutoTokenizer.from_pretrained(
    "tomasonjo/text2cypher-demo-16bit",
)

# COMMAND ----------

# DBTITLE 1,Machine Learning Signature Inferrer
from mlflow.models import infer_signature

input_example = {
        "messages": [
            {"role": "user", "content": "Identify the top 5 questions with the most downVotes."},
        ],
        "max_tokens": 32,
        "temperature": 0.5,
        "top_p": 1,
        "top_k": 1,
        "stop" :"",
        "n": 1,
    }

# COMMAND ----------

# MAGIC %md
# MAGIC To enable optimized serving, when logging the model, include the extra metadata dictionary when calling `mlflow.transformers.log_model` as shown below:
# MAGIC
# MAGIC ```
# MAGIC metadata = {"task": "llm/v1/chat"}
# MAGIC ```
# MAGIC This specifies the API signature used for the model serving endpoint.
# MAGIC

# COMMAND ----------

# DBTITLE 1,Databricks MLflow Model Logging
import mlflow

# Comment out the line below if not using Models in UC 
# and simply provide the model name instead of three-level namespace
mlflow.set_registry_uri('databricks-uc')
CATALOG = "main"
SCHEMA = "jw_graphrag_demo"
registered_model_name = f"{CATALOG}.{SCHEMA}.text2cypher-demo-16bit"

# Start a new MLflow run
with mlflow.start_run():
    components = {
        "model": model,
        "tokenizer": tokenizer,
    }
    mlflow.transformers.log_model(
        transformers_model=components,
        task = "llm/v1/chat",
        artifact_path="model",
        registered_model_name=registered_model_name,
        input_example=input_example
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: View optimization information for your model
# MAGIC
# MAGIC Modify the cell below to change the model name. After calling the model optimization information API, you will be able to retrieve throughput chunk size information for your model. This is the number of tokens/second that corresponds to 1 throughput unit for your specific model.

# COMMAND ----------

import requests
import json

# Name of the registered MLflow model
model_name = registered_model_name

# Get the latest version of the MLflow model
model_version = 1

# Get the API endpoint and token for the current notebook context
API_ROOT = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get() 
API_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

headers = {"Context-Type": "text/json", "Authorization": f"Bearer {API_TOKEN}"}

response = requests.get(url=f"{API_ROOT}/api/2.0/serving-endpoints/get-model-optimization-info/{model_name}/{model_version}", headers=headers)

print(json.dumps(response.json(), indent=4))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Configure and create your model serving GPU endpoint
# MAGIC
# MAGIC Modify the cell below to change the endpoint name. After calling the create endpoint API, the logged Llama2 model is automatically deployed with optimized LLM serving.

# COMMAND ----------

# Set the name of the MLflow endpoint
endpoint_name = "text2cypher-demo-16bit"

# COMMAND ----------

# DBTITLE 1,Databricks Endpoint Deployment Script
from mlflow.deployments import get_deploy_client

!export DATABRICKS_HOST = f"{API_ROOT}/api/2.0/serving-endpoints"
!export DATABRICKS_TOKEN = API_TOKEN

client = get_deploy_client("databricks")

endpoint = client.create_endpoint(
    name=endpoint_name,
    config={
        "served_entities": [
            {
                "entity_name": model_name,
                "entity_version": model_version,
                "min_provisioned_throughput": response.json()['throughput_chunk_size'],
                "max_provisioned_throughput": response.json()['throughput_chunk_size'],
            }
        ]
    },
)

print(json.dumps(endpoint, indent=4))

# COMMAND ----------

# MAGIC %md
# MAGIC ## View your endpoint
# MAGIC To see your more information about your endpoint, go to the **Serving** on the left navigation bar and search for your endpoint name.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Query your endpoint
# MAGIC
# MAGIC Once your endpoint is ready, you can query it by making an API request. Depending on the model size and complexity, it can take 30 minutes or more for the endpoint to get ready.  

# COMMAND ----------

from mlflow.deployments import get_deploy_client

!export DATABRICKS_HOST = f"{API_ROOT}/api/2.0/serving-endpoints"
!export DATABRICKS_TOKEN = API_TOKEN

client = get_deploy_client("databricks")

endpoint = client.create_endpoint(
    name=endpoint_name,
    config={
        "served_entities": [
            {
                "entity_name": model_name,
                "entity_version": model_version,
                "min_provisioned_throughput": response.json()['throughput_chunk_size'],
                "max_provisioned_throughput": response.json()['throughput_chunk_size'],
            }
        ]
    },
)

print(json.dumps(endpoint, indent=4))

# COMMAND ----------

# DBTITLE 1,AI Explanation Request Handler
chat_response = client.predict(
    endpoint=endpoint_name,
    inputs={
        "messages": [
            {
              "role": "user",
              "content": "Identify the top 5 questions with the most downVotes. Just return a cypher query. No explanation please."
            }
        ],
    }
)

print(json.dumps(chat_response, indent=4))
