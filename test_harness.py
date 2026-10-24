from harness_agent.harness import AgentHarness
from llm import get_llm
model = get_llm("qwen/qwen3.8-27b")
# model = get_llm("deepseek")
# model = get_llm("openai/gpt-oss-120b")
# model = get_llm("gpt-6-luna")

harness = AgentHarness(model = model, training_mode=True)

response = harness.invoke("see the available payment options")
print('------------------------------------------------')
print(response)


# response = harness.invoke("do you have info about order 1234?")
# print('------------------------------------------------')
# print(response)
