from crewai import Agent, Crew, Task, LLM
import os
from dotenv import load_dotenv
from tools import click, scroll, type_text, get_next_action, open_application
from pydantic import BaseModel, Field
from typing import List
load_dotenv()
class Output(BaseModel):
    actions : List[str] = Field(description="Actions taken while executing the task")
    tools : List[str] = Field(description="List of tools called eg tool_name() : parameter for tool passed")

my_llm = LLM(
    model="gemini/gemini-1.5-flash",
    temperature=0.7,
    os.environ["GEMINI_API_KEY"]
)

step_reasoner = Agent(
    role = "Windows Automation expert",
    goal = "Your task is to automate the user query as by breaking into steps and handle any unusual scenerio the query is {query}",
    backstory = '''You are an expert in automating windows using user prompts. Having great experience in
    handling complex tasks by breaking it into small steps and highly reliable to complete the task.''',
    llm = my_llm,
    allow_delegation=True,
    tools=[click, scroll, type_text, open_application],
    verbose=True
)

vision = Agent(
    role = "Image reasoning expert",
    goal = '''Your task is to take the current state context given and make reasoning on an image and 
    produce the best next action to achieve the given goal.''',
    backstory = '''You are an expert in processing and reasoning images and taking relevant action after that.
    You are highly reliable and takes actions that are near to perfect.''',
    llm=my_llm,
    allow_delegation=False,
    verbose=True,
    tools=[get_next_action]
)


task1 = Task(
    description=('''Your task is to take the user input and break it into doable steps and execute the
    steps with the help of the tools provided and do not assume anything by yourself rather delegate the task
    appropriate co worker'''),
    agent=step_reasoner,
    expected_output = "The output should include the steps you followed to achieve the task",
    output_pydantic=Output
)

task2 = Task(
    description='''You will be given a current state and using that you have to generate the next set of actions
    do as per instructed and dont assume any action''',
    agent = vision,
    expected_output = "Include the details that you used",
    output_pydantic=Output
)

crew = Crew(
    agents=[step_reasoner, vision],
    tasks = [task1, task2],
    verbose=1,
    planning=True,
    output_log_file="agent.txt"
)


automate = '''add 34 and 77 in calculator'''

result = crew.kickoff(inputs={"query":automate})
print(result.raw)
