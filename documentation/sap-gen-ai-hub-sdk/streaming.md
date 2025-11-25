Streaming
=========

Streaming in AI models enables real-time data generation. With native SDKs, invocation and response formats vary by provider and model. Langchain simplifies this by offering a unified stream method.

Native SDKs
-----------

### OpenAI - ChatGPT

`from gen_ai_hub.proxy.native.openai import chat  def stream_openai(prompt, model_name='gpt-4o-mini'):
 messages = [ {"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt} ]  kwargs = dict(model_name=model_name, messages=messages, max_tokens=500, stream=True) stream = chat.completions.create(**kwargs)  for chunk in stream: if chunk.choices: content = chunk.choices[0].delta.content if content: print(content, end='')` Copy code

`stream_openai("Why is the sky blue?")` Copy code

`The blue color of the sky is due to the scattering of sunlight by molecules and small particles in the Earth's atmosphere. This scattering is more effective for shorter (blue) wavelengths, causing them to be scattered in all directions, thus making the sky appear blue to our eyes.` Copy code

#### Structured model outputs

`from gen_ai_hub.proxy import get_proxy_client from gen_ai_hub.proxy.native.openai import chat, OpenAI from pydantic import BaseModel  class Person(BaseModel):
 name: str age: int  messages = [{"role": "user", "content": "Tell me about John Doe, aged 30."}]  def stream_openai_structured_outputs(messages, response_object, model_name):
 # For more information, see: # https://www.github.com/openai/openai-python#with_streaming_response and # https://platform.openai.com/docs/guides/structured-outputs#streaming with chat.completions.with_streaming_response.parse( model=model_name, messages=messages, response_format=Person ) as stream: response = stream.parse() # takes care of the stream chunks and returns the final response return response.choices[0].message.parsed  print(stream_openai_structured_outputs(messages, Person, "gpt-4o-mini"))` Copy code

`name='John Doe' age=30` Copy code

`def stream_beta_openai_structured_outputs(messages, response_object, model_name):
 chat = OpenAI(proxy_client=get_proxy_client()) with chat.beta.chat.completions.stream( model=model_name, messages=messages, response_format=Person ) as stream: response = stream.get_final_completion() # This will wait for the full response to be received return response.choices[0].message.parsed  print(stream_beta_openai_structured_outputs(messages, Person, "gpt-4o-mini"))` Copy code

`name='John Doe' age=30` Copy code

### Google - Gemini

`from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel from vertexai.generative_models import GenerationConfig   def stream_gemini(prompt, model_name='gemini-2.0-flash'):
 generation_config = GenerationConfig(max_output_tokens=500) model = GenerativeModel(model_name=model_name, generation_config=generation_config) stream = model.generate_content(prompt, stream=True)  for chunk in stream: print(chunk.text, end='')` Copy code

`stream_gemini("Why is the sky blue?")` Copy code

`The sky appears blue due to a phenomenon called **Rayleigh scattering**. Here's a simplified explanation:  * **Sunlight is made up of all colors of the rainbow.** This is why we see a rainbow when sunlight is refracted through water droplets. * **The Earth's atmosphere is filled with tiny particles like nitrogen and oxygen.** These particles are much smaller than the wavelength of visible light. * **When sunlight hits these particles, it gets scattered in all directions.** This is called scattering. * **Blue light has a shorter wavelength than other colors.**  This means it gets scattered more effectively by the tiny particles in the atmosphere. * **As a result, we see more blue light scattered in the sky than other colors.** This is why the sky appears blue during the day.  **Here's an analogy:** Imagine shining a flashlight through a dusty room. The dust particles scatter the light, making the room look hazy. Similarly, the tiny particles in the atmosphere scatter sunlight, giving the sky its blue color.  **A few additional points:**  * The sky appears red at sunset and sunrise because the sunlight has to travel through more atmosphere to reach our eyes. This means more blue light gets scattered away, leaving behind the longer wavelengths of red and orange. * If the atmosphere were very thin or there were no particles in it, the sky would appear black. * The sky appears white on a cloudy day because the clouds are large and reflect all colors of light equally.` Copy code

### Anthropic - Claude

`import json from gen_ai_hub.proxy.native.amazon.clients import Session  def stream_claude(prompt, model_name='anthropic--claude-3-haiku'):
 bedrock = Session().client(model_name=model_name) body = json.dumps({ "max_tokens": 500, "messages": [{"role": "user", "content": prompt}], "anthropic_version": "bedrock-2023-05-31" })  response = bedrock.invoke_model_with_response_stream(body=body) stream = response.get("body")  for event in stream: chunk = json.loads(event["chunk"]["bytes"]) if chunk["type"] == "content_block_delta": print(chunk["delta"].get("text", ""), end="")` Copy code

`stream_claude("Why is the sky blue?")` Copy code

`The sky appears blue primarily due to the way sunlight interacts with the gases in Earth's atmosphere. Here are the main reasons why the sky appears blue:  1. Rayleigh scattering - Shorter wavelengths of visible light (blue and violet) are scattered more easily by the small molecules in the atmosphere, like nitrogen and oxygen. This selective scattering of blue light makes the sky appear blue.  2. Ozone absorption - The ozone layer in the upper atmosphere absorbs a significant amount of ultraviolet radiation from the Sun. This absorption by ozone preferentially removes the shorter violet wavelengths, leaving the blue wavelengths to be scattered, further enhancing the blue color of the sky.  3. Water vapor and particles - Other molecules and particles in the air, like water vapor and dust, also contribute to the scattering of light, but to a lesser degree compared to the Rayleigh scattering of nitrogen and oxygen.  So in summary, the sky appears blue because the atmosphere preferentially scatters the shorter blue wavelengths of sunlight, while allowing the longer red and orange wavelengths to pass through more easily. This effect is most pronounced during the day when the sun is high in the sky.` Copy code

### Amazon - Bedrock

`def stream_bedrock(prompt, model_name='amazon--nova-premier'):
 bedrock = Session().client(model_name=model_name) body = json.dumps({ "inputText": prompt, "textGenerationConfig": { "maxTokenCount": 500 } })  response = bedrock.invoke_model_with_response_stream(body=body) stream = response.get("body")  for event in stream: chunk = json.loads(event["chunk"]["bytes"]) if "outputText" in chunk: print(chunk["outputText"])` Copy code

`stream_bedrock("Why is the sky blue?")` Copy code

`The sky is blue due to the way light interacts with the atmosphere. The atmosphere is made up of different gases, including nitrogen and oxygen. When sunlight hits these gases, it scatters in all directions, but some wavelengths of light are absorbed more strongly than others. The blue light that is scattered has a longer wavelength, while the red light is scattered shorter. This causes the sky to appear blue.` Copy code

Langchain
---------

`from gen_ai_hub.proxy.langchain import init_llm  def stream_langchain(prompt, model_name):
 llm = init_llm(model_name=model_name, max_tokens=500)  for chunk in llm.stream(prompt): print(chunk.content, end='')` Copy code

`stream_langchain("How do airplanes stay in the air?", model_name='gpt-4o-mini')` Copy code

`Airplanes stay in the air through a combination of lift, thrust, and control.  1. Lift: The wings of an airplane are designed to create lift, which is the force that pushes the airplane upward. This is achieved through the shape of the wings and the airflow over them. As the airplane moves forward, the air flowing over the wings creates a difference in air pressure, with lower pressure on top of the wing and higher pressure underneath. This pressure difference generates lift, keeping the airplane in the air.  2. Thrust: Thrust is the force that propels the airplane forward. It is typically generated by the engines, which produce a powerful stream of air or exhaust gases to push the airplane through the air. The combination of lift and thrust allows the airplane to stay airborne and move forward.  3. Control: In addition to lift and thrust, airplanes also rely on control surfaces such as ailerons, elevators, and rudders to maneuver and maintain stability in the air. Pilots use these control surfaces to adjust the airplane's attitude, altitude, and direction.  Overall, the combination of lift, thrust, and control allows airplanes to stay in the air and fly safely to their destinations.` Copy code

`stream_langchain("How do airplanes stay in the air?", model_name='gemini-2.0-flash')` Copy code

`Airplanes stay in the air due to a combination of **lift, thrust, drag, and weight**. Here's a breakdown:  **1. Lift:**  * **Aerodynamics:** The shape of an airplane's wings is designed to create lift. The wings are curved on top and flat on the bottom. This shape causes air to travel faster over the top of the wing than underneath. * **Bernoulli's Principle:** This principle states that as the speed of a fluid (like air) increases, its pressure decreases. The faster air flow over the top of the wing creates lower pressure, while the slower air flow underneath creates higher pressure. This pressure difference creates an upward force called lift. * **Angle of Attack:** The angle at which the wing meets the oncoming air also affects lift. A higher angle of attack creates more lift, but also more drag.  **2. Thrust:**  * **Engines:** Airplane engines provide thrust, the force that propels the plane forward. * **Jet Engines:** These engines take in air, compress it, burn fuel, and then expel hot gases at high speed, creating thrust. * **Propeller Engines:** These engines use a rotating propeller to push air backward, creating thrust.  **3. Drag:**  * **Air Resistance:** Drag is the force that opposes the motion of the airplane through the air. It's caused by friction between the air and the airplane's surface. * **Factors Affecting Drag:**  Drag is affected by the airplane's shape, size, and speed.  **4. Weight:**  * **Gravity:** The weight of the airplane is the force pulling it down towards the Earth due to gravity.  **How it all works together:**  * **Lift and Weight:** For an airplane to fly, the lift force must be greater than the weight force. * **Thrust and Drag:** The thrust force must be greater than the drag force to overcome air resistance and propel the airplane forward.  **In summary:**  Airplanes stay in the air because their wings are designed to create lift, their engines provide thrust, and the combination of these forces overcomes the forces of gravity and drag.` Copy code

`stream_langchain("How do airplanes stay in the air?", model_name='anthropic--claude-3-haiku')` Copy code

`Airplanes stay in the air due to the principles of aerodynamics. The key factors are:  1. Lift: As the airplane moves through the air, the wings generate lift. This lift is created by the difference in air pressure above and below the wings. The curved shape of the wings (airfoil) causes the air to move faster over the top of the wing, resulting in lower pressure. The higher pressure underneath the wing pushes up, creating the lift that counteracts the airplane's weight and keeps it airborne.  2. Thrust: The airplane's engines provide the thrust needed to overcome air resistance (drag) and keep the plane moving forward. The forward motion of the plane generates more lift on the wings.  3. Weight: The weight of the airplane is counteracted by the lift generated by the wings. As long as the lift is greater than the weight, the plane will stay aloft.  4. Drag: Air resistance, or drag, acts against the forward motion of the plane. The shape of the wings and fuselage is designed to minimize drag and optimize lift.  5. Angle of Attack: The angle at which the wings meet the oncoming air (angle of attack) is crucial. A slight upward tilt of the wings creates more lift.  The combination of lift, thrust, weight, and drag allows airplanes to overcome the force of gravity and remain airborne. Pilots and engineers carefully control these factors to ensure safe and efficient flight.` Copy code

`stream_langchain("How do airplanes stay in the air?", model_name='amazon--nova-premier')` Copy code

 `Airplanes stay in the air by creating enough lift to counteract their own weight. This is done by creating a difference in air pressure on the upper and lower surfaces of the wing.`