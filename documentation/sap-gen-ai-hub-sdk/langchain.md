Langchain Integration
=====================

LangChain provides an interface that abstracts provider-specific details into a common interface. Classes like Chat and Embeddings are interchangeable.

The list of the available models can be found here: [Supported Models](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/_reference/README_sphynx.html#supported-models)

Harmonized Model Initialization
-------------------------------

The `init_llm` and `init_embedding_model` functions allow easy initialization of langchain model interfaces in a harmonized way in generative AI hub sdk

`from langchain.prompts import PromptTemplate from langchain_core.output_parsers import StrOutputParser from gen_ai_hub.proxy.langchain.init_models import init_llm  template = """Question: {question}
 Answer: Let's think step by step.""" prompt = PromptTemplate(template=template, input_variables=['question']) question = 'What is a supernova?'  llm = init_llm('meta--llama3.1-70b-instruct', max_tokens=300) chain = prompt | llm | StrOutputParser() response = chain.invoke({'question': question}) print(response)` Copy code

`from gen_ai_hub.proxy.langchain.init_models import init_embedding_model  text = 'Every decoding is another encoding.'  embeddings = init_embedding_model('text-embedding-ada-002') response = embeddings.embed_query(text) print(response)` Copy code

LLM
---

`from langchain import PromptTemplate  from gen_ai_hub.proxy.langchain.openai import OpenAI  # langchain class representing the AICore OpenAI models from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client  proxy_client = get_proxy_client('gen-ai-hub') # non-chat model model_name = "meta--llama3.1-70b-instruct"  llm = OpenAI(proxy_model_name=model_name, proxy_client=proxy_client)  # can be used as usual with langchain  template = """Question: {question}  Answer: Let's think step by step."""  prompt = PromptTemplate(template=template, input_variables=["question"]) llm_chain = prompt | llm  question = "What NFL team won the Super Bowl in the year Justin Bieber was born?"  print(llm_chain.invoke({'question': question}))` Copy code

Chat model
----------

`from langchain.prompts.chat import (
 AIMessagePromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, )  from gen_ai_hub.proxy.langchain.openai import ChatOpenAI from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client  proxy_client = get_proxy_client('gen-ai-hub')  chat_llm = ChatOpenAI(proxy_model_name='gpt-4o-mini', proxy_client=proxy_client) template = 'You are a helpful assistant that translates english to pirate.'  system_message_prompt = SystemMessagePromptTemplate.from_template(template)  example_human = HumanMessagePromptTemplate.from_template('Hi') example_ai = AIMessagePromptTemplate.from_template('Ahoy!') human_template = '{text}'  human_message_prompt = HumanMessagePromptTemplate.from_template(human_template) chat_prompt = ChatPromptTemplate.from_messages(
 [system_message_prompt, example_human, example_ai, human_message_prompt])  chain = chat_prompt | chat_llm  response = chain.invoke({'text': 'I love planking.'}) print(response.content)` Copy code

### Structured model outputs

`from gen_ai_hub.proxy.langchain.openai import ChatOpenAI from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client from langchain.schema import HumanMessage from pydantic import BaseModel  class Person(BaseModel):
 name: str age: int chat_model = ChatOpenAI(proxy_model_name="gpt-4o-mini", proxy_client=get_proxy_client()) chat_model = chat_model.with_structured_output(method="json_schema", schema=Person, strict=True)  message = HumanMessage(content="Tell me about a person named John who is 30") print(chat_model.invoke([message]))` Copy code

Embeddings
----------

`from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client  proxy_client = get_proxy_client('gen-ai-hub')  embedding_model = OpenAIEmbeddings(proxy_model_name='text-embedding-ada-002', proxy_client=proxy_client)  response = embedding_model.embed_query('Every decoding is another encoding.')  #call without passing proxy_client  embedding_model = OpenAIEmbeddings(proxy_model_name='text-embedding-ada-002')  response = embedding_model.embed_query('Every decoding is another encoding.') print(response)` Copy code

Using New Models Before Official SDK Support
============================================

You can use models via Gen AI Hub even before they are officially listed, provided their provider family (e.g., `Google`, `Amazon Bedrock`) is supported.

1.  **Native SDK Clients:**
    
    If using the provider's native SDK (like `boto3`, `vertexai`) through the Gen AI Hub proxy, you can often use the new model name/ID directly with existing client methods.
    
2.  **Langchain Integration (`init_llm`):**
    
    The `init_llm` helper simplifies creating Langchain LLM objects configured for the proxy.
    
    *   **Alternative:** You can always bypass `init_llm` and instantiate the Langchain classes (e.g., `ChatVertexAI`, `ChatBedrock`, `ChatBedrockConverse`) directly.
        
    *   **Bedrock Specifics**:
        
        *   Requires `model_id` in addition to `model_name`. Find IDs [here](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html). `init_llm` automatically selects the appropriate Bedrock API (older Invoke via `ChatBedrock` or newer Converse via `ChatBedrockConverse`) based on known models.
            
        *   **Crucially:** For _new_ Bedrock models or to force a specific API (Invoke/Converse), you must pass the corresponding initialization function (`init_chat_model` or `init_chat_converse_model`) to the `init_func` argument of `init_llm`.
            

`from gen_ai_hub.proxy.langchain.init_models import init_llm # Import specific init functions for overriding Bedrock behavior from gen_ai_hub.proxy.langchain.amazon import (
 init_chat_model as amazon_init_invoke_model, init_chat_converse_model as amazon_init_converse_model ) from gen_ai_hub.proxy.langchain.google_vertexai import init_chat_model as google_vertexai_init_chat_model  # --- Google Example --- llm_google = init_llm(model_name='gemini-newer-version', init_func=google_vertexai_init_chat_model) # Often just needs model_name  # --- Bedrock Example (New Model requiring Converse API) --- model_name_amazon = 'anthropic--claude-newer-version' model_id_amazon = 'anthropic.claude-newer-version-v1:0' # Use actual ID  llm_amazon = init_llm(
 model_name_amazon, model_id=model_id_amazon, init_func=amazon_init_converse_model # Explicitly select Converse API )  # --- Bedrock Example (Explicitly using older Invoke API) --- # llm_amazon_invoke = init_llm( #     'some-model-name', #     model_id='some-model-id', #     init_func=amazon_init_invoke_model # Explicitly select Invoke API # )`