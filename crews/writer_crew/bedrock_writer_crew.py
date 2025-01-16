###########################################################################################
#
# Author: Daniel Tehan
#
# Date: Nov 23, 2024
#
#
#
###########################################################################################
import os
import json
import boto3
import yaml
from pathlib import Path
from dotenv import load_dotenv, find_dotenv


def load_env():
    _ = load_dotenv(find_dotenv('TDTransparent.env'))


class BedrockWriterCrew():

    agents_path = 'src/crews/writer_crew/config/agents.yaml'
    tasks_path = 'src/crews/writer_crew/config/tasks.yaml'
    max_tokens = 20000

    def __init__(self):
        load_env()
        # Create a Path object for the current directory
        current_directory = Path('.')
        print(current_directory.absolute())
        # Change the following to False if a role switch is not required
        roleSwitch = os.getenv("aws_role_switch")

        if roleSwitch == 'True':
            sts_client = boto3.client(
                "sts",
                aws_access_key_id=os.getenv("aws_access_key_id"),
                aws_secret_access_key=os.getenv("aws_secret_access_key"),
                aws_session_token=os.getenv("aws_session_token")
            )

            # assume role with bedrock permissions, you will need to copy your ARN into the RoleArn field below
            assumed_role = sts_client.assume_role(
                RoleArn=os.getenv("aws_role_arn"), RoleSessionName=os.getenv("aws_role_name")
            )
            # get bedrock role credentials
            temp_credentials = assumed_role["Credentials"]
            # create bedrock runtime
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv("aws_region"),
                aws_access_key_id=temp_credentials["AccessKeyId"],
                aws_secret_access_key=temp_credentials["SecretAccessKey"],
                aws_session_token=temp_credentials["SessionToken"],
            )
        else:
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv("aws_region"),
                aws_access_key_id=os.getenv("aws_access_key_id"),
                aws_secret_access_key=os.getenv("aws_secret_access_key"),
                aws_session_token=os.getenv("aws_session_token")
            )

        # Get prompt information from yaml files
        self.agents_config = yaml.safe_load(open(self.agents_path, 'r'))
        self.tasks_config = yaml.safe_load(open(self.tasks_path, 'r'))

        # Get model infomation
        self.crew_type = os.getenv("crew_type")

    def kickoff(self, inputs):
        # Building the system prompt and messages for the bedrock model
        system_prompt = "You are a " + self.agents_config['writer']['role'] + " who will " + \
            self.agents_config['writer']['goal'] + \
            self.agents_config['writer']['backstory']

        # Building the user prompt
        prompt_data = self.tasks_config['writer_task']['description'] + \
            " Expected output will be: " + \
            self.tasks_config['writer_task']['expected_output']
        for key, value in inputs.items():
            prompt_data = prompt_data.replace(key, value)

        # Building the body and invoking the model, returning the LLM text
        # Bedrock Sonnet Model
        if self.crew_type == "Bedrock-Sonnet":
            self.model_id = os.getenv("aws_model_sonnet")
            user_message = {"role": "user", "content": prompt_data}
            messages = [user_message]
            body = json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "system": system_prompt,
                    "messages": messages
                }
            )

            response = self.bedrock_client.invoke_model(
                body=body, modelId=self.model_id, contentType="application/json", accept="application/json"
            )
            response_body = json.loads(response.get('body').read())
            return response_body["content"][0]["text"]

        # Bedrock Llama Models
        elif self.crew_type == "Bedrock-Llama1b" or self.crew_type == "Bedrock-Llama3b":
            if self.crew_type == "Bedrock-Llama1b":
                self.model_id = os.getenv("aws_model_llama1b")
            elif self.crew_type == "Bedrock-Llama3b":
                self.model_id = os.getenv("aws_model_llama3b")

            formated_prompt = f"""
                <|begin_of_text|><|start_header_id|>user<|end_header_id|>
                {system_prompt} {prompt_data}
                <|eot_id|>
                <|start_header_id|>assistant<|end_header_id|>
                """
            body = json.dumps(
                {
                    "prompt": formated_prompt
                }
            )
            response = self.bedrock_client.invoke_model(
                body=body, modelId=self.model_id, contentType="application/json", accept="application/json"
            )
            response_body = json.loads(response.get('body').read())
            return response_body["generation"]

        # Bedrock Nova Models
        elif self.crew_type == "Bedrock-Nova-Micro" or self.crew_type == "Bedrock-Nova-Lite":
            if self.crew_type == "Bedrock-Nova-Micro":
                self.model_id = os.getenv("aws_model_nova_micro")
            elif self.crew_type == "Bedrock-Nova-Lite":
                self.model_id = os.getenv("aws_model_nova_lite")

            message_list = [
                {"role": "user", "content": [{"text": prompt_data}]}]
            system_list = [{"text": system_prompt}]
            additionalModelRequestFields = {
                "inferenceConfig": {
                    "topK": 20
                }
            }
            response_body = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=message_list,
                system=system_list,
                additionalModelRequestFields=additionalModelRequestFields
            )
            return response_body["output"]["message"]["content"][0]["text"]
