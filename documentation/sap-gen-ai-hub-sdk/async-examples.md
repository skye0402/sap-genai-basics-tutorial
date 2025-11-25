Async examples
Async Amazon native
This notebook demonstrates how to use async-based calls for Amazon AI models.

import json
from gen_ai_hub.proxy.native.amazon.clients import AsyncSession

# ### Async Function to Invoke Amazon Model

async def async_bedrock_invoke_model():
    session = AsyncSession()
    bedrock = await session.async_client(model_name="amazon--nova-premier")
    body = json.dumps(
        {
            "inputText": "Explain black holes to 8th graders.",
            "textGenerationConfig": {
                "maxTokenCount": 300,
                "stopSequences": [],
                "temperature": 0.0,
                "topP": 0.9,
            },
        }
    )
    response = await bedrock.invoke_model(body=body)
    response_body = json.loads(await response.get("body").read())
    print("Response:", response_body)
    await bedrock.close()


##%%
# Run the async functions
response = await async_bedrock_invoke_model()
Copy code
Async Function to Stream Amazon Model Response
async def async_bedrock_invoke_with_stream():
    session = AsyncSession()
    bedrock = await session.async_client(model_name="amazon--nova-premier")
    body = json.dumps(
        {
            "inputText": "You are a story teller. Tell me a short story about boats.",
            "textGenerationConfig": {
                "maxTokenCount": 300,
                "stopSequences": [],
                "temperature": 0.0,
                "topP": 0.9,
            },
        }
    )
    async for event in bedrock.invoke_model_with_response_stream(body=body):
        for line in event["chunk"]["bytes"].splitlines():
            if line and line.startswith(b"data: "):
                line = line[6:]
                chunk = json.loads(line)
                if "outputText" in chunk:
                    print("Chunk Output:", chunk["outputText"])

# ### Run Async Functions
await async_bedrock_invoke_with_stream()
Copy code
##%% [markdown]
# ### Async Function to Converse with Amazon Bedrock

##%%
async def async_amazon_bedrock_converse(model_name):
    session = AsyncSession()
    bedrock = await session.async_client(model_name=model_name)
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

    response = await bedrock.converse(
        messages=conversation,
        inferenceConfig={"maxTokens": 512, "temperature": 0.0, "topP": 0.9},
    )
    print("Response:", response["output"]["message"]["content"][0]["text"])
    await bedrock.close()

##%% [markdown]
# ### Run the Async Function

##%%
# Replace with the desired model name
await async_amazon_bedrock_converse("amazon--nova-premier")
Copy code
Async Function to Test Amazon Titan Embedding
async def async_amazon_titan_embedding(model_name):
    session = AsyncSession()
    bedrock = await session.async_client(model_name=model_name)
    body = json.dumps(
        {
            "inputText": "Please recommend books with a theme similar to the movie 'Inception'.",
        }
    )
    response = await bedrock.invoke_model(body=body)
    response_body = json.loads(await response.get("body").read())
    print("Response Metadata:", response["ResponseMetadata"])
    print("Embedding:", response_body["embedding"])
    await bedrock.close()

##%% [markdown]
# ### Run the Async Function

##%%
# Replace with the desired model name
await async_amazon_titan_embedding("amazon--titan-embed-text")
Copy code
Gemini async native example:
This demonstrates how to use the generate_content_async method for the Gemini model.

from vertexai.generative_models import Content, Part, GenerationConfig
from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client


def get_test_messages(text="Write a story about a magic backpack."):
    user_prompt_content = Content(
        role="user",
        parts=[
            Part.from_text(text),
        ],
    )
    return user_prompt_content


async def async_gemini_generate_content(model_name):
    # Initialize the GenerativeModel with the desired configuration
    model = GenerativeModel(
        proxy_client=get_proxy_client(),  # Replace with your proxy client instance
        model_name=model_name,
        generation_config=GenerationConfig(temperature=0),
    )
    try:
        # Prepare the input content
        content = get_test_messages()
        
        # Call the asynchronous generate_content method
        model_response = await model.generate_content_async(content)
        
        print("Generated Content:", model_response.text)
    finally:
        # Ensure the async client is properly closed
        await model._close_async_client()


await async_gemini_generate_content("gemini-2.0-flash")
Copy code
Async Gemini Chat Example
This notebook demonstrates how to use the send_message_async method for the Gemini model.

from vertexai.generative_models import GenerationResponse, GenerationConfig

##%% [markdown]
# ### Async Function to Test Gemini Chat

##%%
async def async_gemini_chat(model_name):
    # Initialize the GenerativeModel with the desired configuration
    model = GenerativeModel(
        proxy_client=None,  # Replace with your proxy client instance
        model_name=model_name,
        generation_config=GenerationConfig(temperature=0)
    )
    try:
        # Start a chat session
        chat_session = model.start_chat()

        # Send asynchronous messages
        model_response = await chat_session.send_message_async("Hello.")
        print("Response 1:", model_response.text)

        model_response = await chat_session.send_message_async(
            "What is your opinion about the latest Gemini model?"
        )
        print("Response 2:", model_response.text)
    finally:
        # Ensure the async client is properly closed
        await model._close_async_client()

##%% [markdown]
# ### Run the Async Function

##%%
# Replace with the desired model name
await async_gemini_chat("gemini-2.0-flash")
Copy code
Async Gemini Stream Generate Content Example
This demonstrates how to use the generate_content_async method with stream=True for the Gemini model.

from vertexai.generative_models import GenerationConfig

##%% [markdown]
# ### Async Function to Stream Generate Content

##%%
async def async_gemini_stream_generate_content(model_name):
    # Initialize the GenerativeModel with the desired configuration
    model = GenerativeModel(
        model_name=model_name,
        generation_config=GenerationConfig(temperature=0)
    )
    try:
        # Prepare the input content
        content = get_test_messages(
            text="You are a story teller. Write a paragraph about a magic kingdom."
        )
        # Call the asynchronous generate_content method with streaming enabled
        async_response_stream = await model.generate_content_async(content, stream=True)

        # Process and print each chunk of the streamed response
        async for chunk in async_response_stream:
            print("Chunk:", chunk.text)
    finally:
        # Ensure the async client is properly closed
        await model._close_async_client()

##%%
# Replace with the desired model name
await async_gemini_stream_generate_content("gemini-2.0-flash")
Copy code
Langchain examples
Async Chat Model Example This demonstrates how to use the chat_model.ainvoke method for the Claude model.

from langchain_core.messages import HumanMessage, AIMessage
from gen_ai_hub.proxy.langchain.amazon import ChatBedrock

async def async_amazon_chat_model():
    # Initialize the ChatBedrock model with the desired configuration
    chat_model = ChatBedrock(
        model_name="anthropic--claude-3-haiku",
        model_kwargs={"temperature": 0.0}
    )
    # Send a message to the model
    response = await chat_model.ainvoke(
        [HumanMessage(content="Write me a song about sparkling water.")]
    )
    # Validate and print the response
    if isinstance(response, AIMessage):
        print("Response:", response.content)

await async_amazon_chat_model()
Copy code
Async Chat Streaming Example
This notebook demonstrates how to use the chat_model.astream method for the Claude model.

from langchain.schema import HumanMessage
from langchain_core.messages import AIMessageChunk
from gen_ai_hub.proxy.langchain.amazon import ChatBedrock

async def async_chat_streaming():
    # Initialize the ChatBedrock model with streaming enabled
    chat_model = ChatBedrock(
        model_name="anthropic--claude-3-haiku",
        model_kwargs={"temperature": 0.0},
        proxy_client=None,  # Replace with your proxy client instance
        streaming=True
    )
    chunks = []
    # Stream responses asynchronously
    async for chunk in chat_model.astream([HumanMessage(content="Write me a song about sparkling water in 20 words.")]):
        chunks.append(chunk)
        print(chunk.content)  # Print each chunk's content
    # Validate that all chunks are instances of AIMessageChunk
    assert all(isinstance(chunk, AIMessageChunk) for chunk in chunks)


await async_chat_streaming()
Copy code
Chat Converse Model Example
This demonstrates how to use the ChatBedrockConverse model's ainvoke .

from gen_ai_hub.proxy.langchain.amazon import ChatBedrockConverse

async def chat_converse_model_example(model_name):
    try:
        # Initialize the ChatBedrockConverse model
        chat_model = ChatBedrockConverse(
            model_name=model_name,
            model_kwargs={"temperature": 0.0}
        )
        # Send a message to the model
        response = await chat_model.ainvoke(
            [HumanMessage(content="Write me a song about sparkling water.")]
        )
        # Check if the response is valid
        if isinstance(response, AIMessage):
            print("Response:", response.content)
        else:
            print("Unexpected response type:", type(response))
    except Exception as e:
        print(f"An error occurred: {e}")


await chat_converse_model_example("anthropic--claude-3-haiku")
Copy code
Async Gemini Model Invocation Example
This demonstrates how to use the ainvoke method of the Gemini model asynchronously.

from gen_ai_hub.proxy.langchain import init_llm

async def gemini_ainvoke_example():
    # Initialize the model using init_llm
    llm = init_llm(
        model_name="gemini-2.0-flash",
        max_tokens=300
    )
    # Send a message to the model
    response = await llm.ainvoke("Write a ballad about LangChain")
    print(response)

await gemini_ainvoke_example()
Copy code
from langchain_core.messages import AIMessage
from gen_ai_hub.proxy.langchain.google_vertexai import ChatVertexAI

async def gemini_ainvoke_example():
    # Initialize the ChatVertexAI model
    chat_model = ChatVertexAI(
        proxy_model_name="gemini-2.0-flash",
        max_tokens=300
    )
    # Send a message to the model
    response = await chat_model.ainvoke("Write a ballad about LangChain")
    print(response)

await gemini_ainvoke_example()
Copy code
Async Gemini Streaming Example
This notebook demonstrates how to use the astream method of the Gemini chat model asynchronously.

async def gemini_astream_example():
        # Initialize the ChatVertexAI model
        chat_model = ChatVertexAI(
            proxy_model_name="gemini-2.0-flash",
            temperature=0
        )
        # Define the input content
        content = "You are a storyteller. Write a story about a magic backpack."
        # Stream the response
        async for chunk in chat_model.astream(content):
            print("Chunk:", chunk.content)

await gemini_astream_example()