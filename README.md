# Build a Business Definition for a database schema

Author: Daniel Tehan
Date: Jan 2025

## Process
Ensure that the environment variables are set in getflow.env file, this will contain the LLM keys, model name, and database credential location

The entire flow of the process is controlled using crewai flow.
1. Gets the database credentials
2. Connects to the database
3. Gets a list of tables from the schema identifed in the credentials
4. Connects to the database and gets create table definitions and sample of 3 rows of data
5. Connects to a large language model and builds 
    - writer: the business definition report for the tables in the schema in a markup report
   


## Configuration

**Open AI Version**
- This version requires an Open AI key to be in the DBCatalog.env file. GPT 4o mini is fast, comprehensive and reasonable price.

**Bedrock Sonet version**
- This requires a set of AWS keys to be defined in the DBCatalog.env file.  Sonet 3.5 does a comprehensive job, but is slow and more expensive.

**Bedrock Llama version**
- This requires a set of AWS keys to be defined in the DBCatalog.env file. Llama 3.2 3B or Llama 3.2 1B model is fast and cheap, not a lot of details in the descriptions. 

**Bedrock Nova version**
- This requires a set of AWS keys to be defined in the DBCatalog.env file. Nova Micro and Nova Lite model is fast and cheap. 

**Azure OpenAI version**
- This requires a set of Azure keys to be defined in the DBCatalog.env file. GPT 4o mini is fast, comprehensive and reasonable price.


DBCatalog.env file configuration shown below

```
##################################################
# Application configuration
##################################################
# Crew types supported are: Bedrock-Sonnet, Bedrock-Llama1b, Bedrock-Llama3b, Bedrock-Nova-Micro, Bedrock-Nova-Lite, Azure-GPT, OpenAI
crew_type=Azure-GPT


##################################################
# AWS Config
##################################################
aws_access_key_id=
aws_secret_access_key=
aws_session_token=

# AWS region should be selected
aws_region=us-east-1
# Used to Swith to another AWS role, if this is not used change aws_role_switch=False
aws_role_switch=True
aws_role_arn=
aws_role_name=

# Models supported, do not change
aws_model_sonnet=anthropic.claude-3-5-sonnet-20240620-v1:0
aws_model_llama3b=us.meta.llama3-2-3b-instruct-v1:0
aws_model_llama1b=us.meta.llama3-2-1b-instruct-v1:0
aws_model_nova_micro=us.amazon.nova-micro-v1:0
aws_model_nova_lite=us.amazon.nova-lite-v1:0


##################################################
# Azure keys should be inserted below if using Azure AI
# please use URL engpoint for model
##################################################

azure_api_version=2023-07-01-preview
azure_endpoint=
azure_api_key=
azure_model_gpt-4o-mini=gpt-4o-mini

azure_embed_endpoint=
azure_embed_api_key=
```


## Directory structure

**Core Directories**

[./](./)
- root directory for the application 
- contains main.py 
- contains requirements.txt, used in installing environment
- contains README.md

[./chromadb/](./chomadb/) 
- contains the vector database for semmantic search

[./instance/](./instance/)
- contains the database containing the table descriptions

[./website/](./website/)
- contains the flask website for the application

**Database Writer Directories**

[./crews/writer_crew/](./crews/writer_crew/)
- bedrock_writer_crew.py 
- azure_writer_crew.py

[./crews/writer_crew/config/](./crews/writer_crew/config/)
- agents.yaml contains the agent definition
- tasks.yaml contains the task definition, including prompt

[./crews/writer_crew/Output](./crews/writer_crew/Output)
- contains the generated database description for the schemas, example output is provided


## Setup
pip install the following packages into your python3.11 environment
- refer to the requirements.txt file for all required packages

**On Linux/Mac:**
```
git clone https://github.com/dtehan/DBCatalog.git
cd DBCatalog
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt 
source venv/bin/activate
```

**On Windows**
```
git clone https://github.com/dtehan/DBCatalog.git
cd DBCatalog
python3.11 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt 
venv\Scripts\activate
```

## Running
**Run this project**
```
venv/bin/python main.py
```


