# Databricks notebook source
# MAGIC %md
# MAGIC # Track, serve and monitor the GraphRAG app via the Mosaic AI framework
# MAGIC
# MAGIC **Mosaic AI Agent Framework** and **MLflow** provide tools to help you author enterprise-ready agents in Python. Databricks supports authoring agents using third-party agent authoring libraries like LangChain, LlamaIndex, or custom Python implementations.
# MAGIC In this notebook we will will:
# MAGIC
# MAGIC * Log the GraphRAG model
# MAGIC * Register it in Unity Catalog
# MAGIC * Deploy it to a serving endpoint
# MAGIC * Deploy the review app so you can test it and review the answers
# MAGIC

# COMMAND ----------

# MAGIC %pip install -q -U databricks-agents python-dotenv neo4j langchain-openai mlflow mlflow-skinny langchain==0.2.1 langchain_core==0.2.5 langchain_community==0.2.4

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./Config

# COMMAND ----------

import mlflow
import os
import time
from dotenv import load_dotenv
from databricks import agents
from databricks.sdk.service.serving import EndpointStateReady, EndpointStateConfigUpdate
from databricks.sdk import WorkspaceClient
from mlflow.models.signature import ModelSignature
from mlflow.models.rag_signatures import StringResponse, ChatCompletionRequest, ChatCompletionResponse
from mlflow.models.resources import DatabricksServingEndpoint

# COMMAND ----------

load_dotenv()

# COMMAND ----------

# Start an MLflow run with a specified run name from environment variables
with mlflow.start_run(run_name=os.getenv('MLFLOW_RUN_NAME')):
    # Log a LangChain model to MLflow
    logged_chain_info = mlflow.langchain.log_model(
        lc_model=os.path.join(
            os.getcwd(),
            "3 - Create the GraphRAG Chatbot",  # Path to the Notebook of the LangChain model
        ),
        artifact_path="chain",  # Path where the model artifacts will be stored
        model_config={
            'system_prompt': os.getenv('SYSTEM_PROMPT'),  # System prompt configuration
            'llm_model': os.getenv('LLM_MODEL_SERVING_ENDPOINT_NAME'),  # LLM model serving endpoint name
            'llm_model_temperature': os.getenv('LLM_MODEL_TEMPERATURE')  # LLM model temperature setting
        },
        example_no_conversion=True,  # Required by MLflow to use the input_example as the chain's schema
        conda_env={
            "dependencies": [
                {
                    "pip": [
                        "python-dotenv",
                        "langchain==0.2.1",
                        "langchain-community==0.2.4",
                        "langchain-core==0.2.5",
                        # "langchain-databricks",
                        "langchain-openai",
                        "neo4j"
                    ],
                },
            ],
        },
        code_paths=[".env"],
        input_example={
            'query': "Can you show potiential attack paths in our network? Return the first five results"
        },
        resources=[
            DatabricksServingEndpoint(endpoint_name="databricks-meta-llama-3-70b-instruct"),
            DatabricksServingEndpoint(endpoint_name="text2cypher-demo-16bit"),
        ]
    )

# COMMAND ----------

UC_MODEL_NAME = f"{catalog_name}.default.graphrag_bot"  # Define the model name using the catalog name

w = WorkspaceClient()  # Initialize the WorkspaceClient

mlflow.set_registry_uri('databricks-uc')  # Set the MLflow registry URI to Databricks Unity Catalog

# Register the model in the MLflow registry and get the registered model info
uc_registered_model_info = mlflow.register_model(model_uri=logged_chain_info.model_uri, name=UC_MODEL_NAME)

# Deploy the registered model and get the deployment info
deployment_info = agents.deploy(model_name=UC_MODEL_NAME, model_version=uc_registered_model_info.version)

print("\nWaiting for endpoint to deploy. This can take 10 - 30 minutes.")  # Inform the user about the deployment wait time

# Poll the endpoint status until it is ready
while w.serving_endpoints.get(deployment_info.endpoint_name).state.config_update == EndpointStateConfigUpdate.IN_PROGRESS:
    print(".", end="")  # Print a dot to indicate progress
    time.sleep(30)  # Wait for 30 seconds before checking the status again
if w.serving_endpoints.get(deployment_info.endpoint_name).state.ready == EndpointStateReady.NOT_READY:
    print("\nErrors during the deployment, please check the logs")
else:
    print("\nEndpoint is ready")

# COMMAND ----------

# Add the user-facing instructions to the Review App
instructions_to_reviewer = """# GrapRAG bot based on Bloodhound dataset

![BloodHound Logo](https://guides.neo4j.com/sandbox/cybersecurity/img/bloodhound.png)

The source code of the demo is available on [GitHub](https://github.com/conker84/dbx-bloodhound-demo)

We have considered below sample objects for this use case.

- User
- Computer
- Group
- Domain
- Group Policy Object (GPO) - Virtual Collection of Policy Settings
- OU (Organization Unit) - Sub division

![Graph Model](https://guides.neo4j.com/sandbox/cybersecurity/img/model.svg)
"""
agents.set_review_instructions(UC_MODEL_NAME, instructions_to_reviewer)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Example of the review app
# MAGIC The expected view from the review app should be like the following:
# MAGIC
# MAGIC <img src="images/review-app-intro.png">
# MAGIC
# MAGIC and
# MAGIC
# MAGIC <img src="images/review-app-example.png">
