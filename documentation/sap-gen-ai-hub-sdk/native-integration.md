Our SDK offers a developer-friendly way to consume foundational models available in the SAP generative AI hub. We strive to facilitate seamless interactions with these models by providing integrations that act as drop-in replacements for the native client SDKs and LangChain. This allows developers to use familiar interfaces and workflows. Usage is as follows.

Native Client Integrations
As of now, there are integrations with three types of native client SDKs (OpenAI, Google, Amazon).

The following contains at least one example per SDK. Note: Some providers share the same interface and can be consumed using the same api. For example, Anthropic Claude and Amazon Nova can be used with the Amazon api.

The list of the available models can be found here: Supported Models

Completions
OpenAI
Completions equivalent to openai.Completions. Below is an example usage of Completions in generative AI hub sdk. All models that support the legacy completion endpoint can be used.

from gen_ai_hub.proxy.native.openai import completions

response = completions.create(
    model_name="meta--llama3.1-70b-instruct",
    prompt="The Answer to the Ultimate Question of Life, the Universe, and Everything is",
    max_tokens=20,
    temperature=0
)
print(response)
Copy code
ChatCompletions equivalent to openai.ChatCompletions Below is an example usage of ChatCompletions in generative AI hub sdk.

from gen_ai_hub.proxy.native.openai import chat

messages = [{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
            {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
            {"role": "user", "content": "Do other Azure Cognitive Services support this too?"}]

kwargs = dict(model_name='gpt-4o-mini', messages=messages)
response = chat.completions.create(**kwargs)

print(response)
Copy code
#example where deployment_id is passed instead of model_name parameter

from gen_ai_hub.proxy.native.openai import chat

messages = [{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
            {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
            {"role": "user", "content": "Do other Azure Cognitive Services support this too?"}]

response = chat.completions.create(deployment_id="dcef02e219ae4916", messages=messages)
print(response)
Copy code
Structured model outputs
LLM output as json objects is a powerful feature that allows you to define the structure of the output you expect from the model.

see https://platform.openai.com/docs/guides/structured-outputs/examples

from pydantic import BaseModel
from gen_ai_hub.proxy.native.openai import chat

class Person(BaseModel):
    name: str
    age: int

response = chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me about John Doe, aged 30."}],
    response_format=Person
)
person = response.choices[0].message.parsed  # Fully typed Person
print(person)
Copy code
Google Vertex AI
Generate Content

from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

proxy_client = get_proxy_client('gen-ai-hub')
kwargs = dict({'model_name': 'gemini-2.5-flash'})
model = GenerativeModel(proxy_client=proxy_client, **kwargs)
content = [{
    "role": "user",
    "parts": [{
        "text": "Write a short story about a magic kingdom."
    }]
}]
model_response = model.generate_content(content)
print(model_response)
Copy code
Function calling of Gemini model using start_chat

from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel
# According to Gemini API it is recommended to use function_calling via chat interface, as this captures user-model back-and-forth interaction.

# example 1 of function calling using start_chat
def multiply(a:float, b:float):
    """returns a * b."""
    return a*b

kwargs = {'model_name': 'gemini-2.5-flash'}
model = GenerativeModel(**kwargs)
chat = model.start_chat(enable_automatic_function_calling=True)
prompt = 'I have 6 cats, each owns 2 mittens, how many mittens is that in total?'
response = chat.send_message(prompt, tools=[multiply])

print(response)
for content in chat.history:
    part = content.parts[0]
    print(content.role, "->", type(part).to_dict(part))
    print('-'*80)
Copy code
# example 2 of function calling using start_chat

def start_music(energetic: bool, loud: bool, bpm: int) -> str:
    """Play some music matching the specified parameters.

    Args:
      energetic: Whether the music is energetic or not.
      loud: Whether the music is loud or not.
      bpm: The beats per minute of the music.

    Returns: The name of the song being played.
    """
    print(f"Starting music! {energetic=} {loud=}, {bpm=}")
    return "Never gonna give you up."


def dim_lights(brightness: float) -> bool:
    """Dim the lights.

    Args:
      brightness: The brightness of the lights, 0.0 is off, 1.0 is full.
    """
    print(f"Lights are now set to {brightness:.0%}")
    return True

tools = [start_music, dim_lights]
kwargs = {'model_name': 'gemini-2.5-flash'}
model = GenerativeModel(**kwargs)
chat = model.start_chat()

prompt = "Turn this place into a party!"
response = chat.send_message(prompt, tools=[tools])
print(response)
prompt = "Music played should be energetic"
response = chat.send_message(prompt, tools=[tools])
print(response)
prompt = "Light should dim"
response = chat.send_message(prompt, tools=[tools])
print(response)
Copy code
Amazon
Invoke Model

import json
from gen_ai_hub.proxy.native.amazon.clients import Session

bedrock = Session().client(model_name="amazon--nova-premier")
body = json.dumps(
    {
        "inputText": "Explain black holes in astrophysics to 8th graders.",
        "textGenerationConfig": {
            "maxTokenCount": 3072,
            "stopSequences": [],
            "temperature": 0.7,
            "topP": 0.9,
        },
    }
)
response = bedrock.invoke_model(body=body)
response_body = json.loads(response.get("body").read())
print(response_body)
Copy code
Converse

from gen_ai_hub.proxy.native.amazon.clients import Session

bedrock = Session().client(model_name="anthropic--claude-4-sonnet")
conversation = [
    {
        "role": "user",
        "content": [
            {
                "text": "Describe the purpose of a 'hello world' program in one line."
            }
        ],
    }
]
response = bedrock.converse(
    messages=conversation,
    inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
)
print(response)
Copy code
Embeddings
OpenAI
Embeddings are equivalent to openai.Embeddings. See below examples of how to use Embeddings in generative AI hub sdk.

from gen_ai_hub.proxy.native.openai import embeddings

response = embeddings.create(
    input="Every decoding is another encoding.",
    model_name="text-embedding-ada-002"
)
print(response.data)
Copy code
from gen_ai_hub.proxy.native.openai import embeddings
# example with encoding format passed as parameter
response = embeddings.create(
    input="Every decoding is another encoding.",
    model_name="text-embedding-ada-002",
    encoding_format='base64'
)
print(response.data)
Copy code
Amazon
import json
from gen_ai_hub.proxy.native.amazon.clients import Session
bedrock = Session().client(model_name="amazon--nova-premier")
body = json.dumps(
    {
        "inputText": "Please recommend books with a theme similar to the movie 'Inception'.",
    }
)
response = bedrock.invoke_model(
    body=body,
)
response_body = json.loads(response.get("body").read())
print(response_body)
Copy code
from gen_ai_hub.proxy.native.openai import embeddings
# example with encoding format passed as parameter
response = embeddings.create(
    input="Every decoding is another encoding.",
    model_name="text-embedding-ada-002",
    encoding_format='base64'
)
print(response.data)
Copy code
Langchain Integration
LangChain provides an interface that abstracts provider-specific details into a common interface. Classes like Chat and Embeddings are interchangeable.

The list of the available models can be found here: Supported Models

Harmonized Model Initialization
The init_llm and init_embedding_model functions allow easy initialization of langchain model interfaces in a harmonized way in generative AI hub sdk

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from gen_ai_hub.proxy.langchain.init_models import init_llm

template = """Question: {question}
    Answer: Let's think step by step."""
prompt = PromptTemplate(template=template, input_variables=['question'])
question = 'What is a supernova?'

llm = init_llm('meta--llama3.1-70b-instruct', max_tokens=300)
chain = prompt | llm | StrOutputParser()
response = chain.invoke({'question': question})
print(response)
Copy code
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model

text = 'Every decoding is another encoding.'

embeddings = init_embedding_model('text-embedding-ada-002')
response = embeddings.embed_query(text)
print(response)
Copy code
LLM
from langchain import PromptTemplate

from gen_ai_hub.proxy.langchain.openai import OpenAI  # langchain class representing the AICore OpenAI models
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

proxy_client = get_proxy_client('gen-ai-hub')
# non-chat model
model_name = "meta--llama3.1-70b-instruct"

llm = OpenAI(proxy_model_name=model_name, proxy_client=proxy_client)  # can be used as usual with langchain

template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate(template=template, input_variables=["question"])
llm_chain = prompt | llm

question = "What NFL team won the Super Bowl in the year Justin Bieber was born?"

print(llm_chain.invoke({'question': question}))
Copy code
Chat model
from langchain.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

proxy_client = get_proxy_client('gen-ai-hub')

chat_llm = ChatOpenAI(proxy_model_name='gpt-4o-mini', proxy_client=proxy_client)
template = 'You are a helpful assistant that translates english to pirate.'

system_message_prompt = SystemMessagePromptTemplate.from_template(template)

example_human = HumanMessagePromptTemplate.from_template('Hi')
example_ai = AIMessagePromptTemplate.from_template('Ahoy!')
human_template = '{text}'

human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, example_human, example_ai, human_message_prompt])

chain = chat_prompt | chat_llm

response = chain.invoke({'text': 'I love planking.'})
print(response.content)
Copy code
Structured model outputs
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from langchain.schema import HumanMessage
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
chat_model = ChatOpenAI(proxy_model_name="gpt-4o-mini", proxy_client=get_proxy_client())
chat_model = chat_model.with_structured_output(method="json_schema", schema=Person, strict=True)

message = HumanMessage(content="Tell me about a person named John who is 30")
print(chat_model.invoke([message]))
Copy code
Embeddings
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

proxy_client = get_proxy_client('gen-ai-hub')

embedding_model = OpenAIEmbeddings(proxy_model_name='text-embedding-ada-002', proxy_client=proxy_client)

response = embedding_model.embed_query('Every decoding is another encoding.')

#call without passing proxy_client

embedding_model = OpenAIEmbeddings(proxy_model_name='text-embedding-ada-002')

response = embedding_model.embed_query('Every decoding is another encoding.')
print(response)
Copy code
Using New Models Before Official SDK Support
You can use models via Gen AI Hub even before they are officially listed, provided their provider family (e.g., Google, Amazon Bedrock) is supported.

Native SDK Clients:

If using the provider's native SDK (like boto3, vertexai) through the Gen AI Hub proxy, you can often use the new model name/ID directly with existing client methods.

Langchain Integration (init_llm):

The init_llm helper simplifies creating Langchain LLM objects configured for the proxy.

Alternative: You can always bypass init_llm and instantiate the Langchain classes (e.g., ChatVertexAI, ChatBedrock, ChatBedrockConverse) directly.

Bedrock Specifics:

Requires model_id in addition to model_name. Find IDs here. init_llm automatically selects the appropriate Bedrock API (older Invoke via ChatBedrock or newer Converse via ChatBedrockConverse) based on known models.

Crucially: For new Bedrock models or to force a specific API (Invoke/Converse), you must pass the corresponding initialization function (init_chat_model or init_chat_converse_model) to the init_func argument of init_llm.

from gen_ai_hub.proxy.langchain.init_models import init_llm
# Import specific init functions for overriding Bedrock behavior
from gen_ai_hub.proxy.langchain.amazon import (
    init_chat_model as amazon_init_invoke_model,
    init_chat_converse_model as amazon_init_converse_model
)
from gen_ai_hub.proxy.langchain.google_vertexai import init_chat_model as google_vertexai_init_chat_model

# --- Google Example ---
llm_google = init_llm(model_name='gemini-newer-version', init_func=google_vertexai_init_chat_model) # Often just needs model_name

# --- Bedrock Example (New Model requiring Converse API) ---
model_name_amazon = 'anthropic--claude-newer-version'
model_id_amazon = 'anthropic.claude-newer-version-v1:0' # Use actual ID

llm_amazon = init_llm(
    model_name_amazon,
    model_id=model_id_amazon,
    init_func=amazon_init_converse_model # Explicitly select Converse API
)

# --- Bedrock Example (Explicitly using older Invoke API) ---
# llm_amazon_invoke = init_llm(
#     'some-model-name',
#     model_id='some-model-id',
#     init_func=amazon_init_invoke_model # Explicitly select Invoke API
# )