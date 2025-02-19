<img src=https://raw.githubusercontent.com/databricks-industry-solutions/.github/main/profile/solacc_logo.png width="600px">

[![DBR](https://img.shields.io/badge/DBR-CHANGE_ME-red?logo=databricks&style=for-the-badge)](https://docs.databricks.com/release-notes/runtime/CHANGE_ME.html)
[![CLOUD](https://img.shields.io/badge/CLOUD-CHANGE_ME-blue?logo=googlecloud&style=for-the-badge)](https://databricks.com/try-databricks)

## Business Problem
This repo is part of the blog article (link to be added), talking about how to combine the Databricks Platform and the Mosaic AI framework components with the Neo4j Graph Database in order to create a cutting edge GraphRAG based chatbot.. In this repo, we’ll highlight how to build and deploy a Knowledge Graph RAG (GraphRAG) system on Databricks and Neo4j using Langchain. We’ll cover how to build a knowledge graph database from structured data in Unity Catalog, general approaches when working with structured (or unstructured) data, the underlying models used for translating text to graph query language, and how to deploy an end-to-end system using Databricks model serving. We will use a cybersecurity example with the open-source data, showing how GraphRAG can help SOC analysts process massive volumes of alerts and identify intricate threat patterns.

## Reference Architecture


## Authors
<andrea.santurbano@databricks.com>

<chandhana.padmanabhan@databricks.com>

<jiayi.wu@databricks.com> 

<dan.pechi@databricks.com>

## Project support 

Please note the code in this project is provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs). They are provided AS-IS and we do not make any guarantees of any kind. Please do not submit a support ticket relating to any issues arising from the use of these projects. The source in this project is provided subject to the Databricks [License](./LICENSE.md). All included or referenced third party libraries are subject to the licenses set forth below.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo. They will be reviewed as time permits, but there are no formal SLAs for support. 

## License

&copy; 2024 Databricks, Inc. All rights reserved. The source in this notebook is provided subject to the Databricks License [https://databricks.com/db-license-source].  All included or referenced third party libraries are subject to the licenses set forth below.

| library                                | description             | license    | source                                              |
|----------------------------------------|-------------------------|------------|-----------------------------------------------------|
| python-dotenv         | Reads key-value pairs from a `.env` file and sets them as environment variables. | MIT        | [GitHub](https://github.com/theskumar/python-dotenv)                                      |
| neo4j                 | Official driver for connecting to Neo4j graph database from Python applications. | Apache-2.0 | [GitHub](https://github.com/neo4j/neo4j-python-driver)                                    |
| langchain-openai      | Integration of OpenAI's API with LangChain for advanced language model applications. | MIT        | [GitHub](https://github.com/hwchase17/langchain/tree/master/libs/langchain-openai)        |
| databricks-agents     | Tools and integrations for building AI agents on the Databricks platform.    | Apache-2.0 | [GitHub](https://github.com/databricks/databricks-agents)                                 |
| mlflow                | Platform for managing the ML lifecycle, including experimentation, reproducibility, and deployment. | Apache-2.0 | [GitHub](https://github.com/mlflow/mlflow)                                                |
| mlflow-skinny         | A lightweight version of MLflow without SQL storage, server, or UI dependencies. | Apache-2.0 | [PyPI](https://pypi.org/project/mlflow-skinny/)                                           |
| langchain             | Framework for developing applications powered by language models.            | MIT        | [GitHub](https://github.com/hwchase17/langchain)                                          |
| langchain_core        | Core components of the LangChain framework.                                  | MIT        | [GitHub](https://github.com/hwchase17/langchain/tree/master/libs/langchain_core)          |
| langchain_community   | Community-driven extensions and integrations for LangChain.                  | MIT        | [GitHub](https://github.com/hwchase17/langchain/tree/master/libs/langchain_community)     |
| transformers          | Library providing thousands of pretrained models for natural language processing tasks. | Apache-2.0 | [GitHub](https://github.com/huggingface/transformers)                                     |
| accelerate            | Simplifies training and inference across multiple devices for PyTorch models. | Apache-2.0 | [GitHub](https://github.com/huggingface/accelerate)                                       |
| unsloth               | Accelerates fine-tuning of large language models by 2-5x with reduced memory usage. | Apache-2.0 | [GitHub](https://github.com/unslothai/unsloth)                                            |
| xformers              | A collection of optimized transformer building blocks for efficient model training. | Apache-2.0 | [GitHub](https://github.com/facebookresearch/xformers)                                    |
| trl                   | Library for training transformer language models with reinforcement learning. | Apache-2.0 | [GitHub](https://github.com/huggingface/trl)                                              |
| peft                  | Implements parameter-efficient fine-tuning methods for large language models. | Apache-2.0 | [GitHub](https://github.com/huggingface/peft)                                             |
| bitsandbytes          | Provides 8-bit optimizers and matrix multiplication routines for efficient training. | MIT        | [GitHub](https://github.com/TimDettmers/bitsandbytes)                                     |

