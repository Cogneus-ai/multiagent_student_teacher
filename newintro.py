import os
import openai
import dotenv
import time
import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import PDFSearchTool
from langchain_openai import ChatOpenAI
from PyPDF2 import PdfReader
from crewai_tools import BaseTool
from crewai_tools import TXTSearchTool
from crewai_tools import FileReadTool
from crewai_tools import Tool
import openai
dotenv.load_dotenv()
def my_intermediate_step_callback(agent, task, step_info):
    st.write(f"Step reached in task: {task.description}, Agent: {agent.role}, Step info: {step_info}")
class ShepherdInputTool(Tool):
    def __init__(self):
        super().__init__(
            name="Shepherd Input Tool",
            description="Tool for collecting input from Shepherd (human student).",
            func=self.get_shepherd_input
        )

    # Method to get input from Shepherd (human student)
    def get_shepherd_input(self, message: str = "Please provide input:", **kwargs):
        # Generate a unique key for the text input
        unique_key = f"shepherd_input_{time.time()}"  # or use any unique identifier you prefer
        return st.text_input(message, key=unique_key)
# Initialize input tools
shepherd_input_tool = ShepherdInputTool()
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"
file_read_tool = FileReadTool()
file_paths1 = [
     '/home/shovan/Videos/shepherdpreassessment.txt',
]

lessonplanner_agent = Agent(
    role="You are a LessonPlanner_Agent with extensive knowledge in geometry."
         "You are given a preassessmentfile of a human student,which is find in the {file_paths1}"
         "you will read this preassessmentfile carefully and analyze to identify the questions the human student could not answer."
         "Based on these unanswered questions, you will create an initial lesson plan and provide this initial lessonplan to the assessor_agent and teachers_agent"
         "When the teachers_agent asks you to update the lesson plan,"
         "you will revise it according to the human student's interests,"
         "which the teachers_agent will provide to you."
         "After updating, you will share the revised lesson plan with the teachers_agent.",
    goal="You are a LessonPlanner_Agent with extensive knowledge in geometry."
         "You are given a preassessmentfile of a human student,which is find in the {file_paths1}"
         "you will read this preassessmentfile carefully and analyze to identify the questions the human student could not answer."
         "Based on these unanswered questions, you will create an initial lesson plan."
         "When the teachers_agent asks you to update the lesson plan,"
         "you will revise it according to the human student's interests,"
         "which the teachers_agent will provide to you."
         "After updating, you will share the revised lesson plan with the teachers_agent.",
    backstory= "You are a LessonPlanner_Agent with extensive knowledge in geometry."
         "You are given a preassessmentfile of a human student,which is find in the {file_paths1}"
         "you will read this preassessmentfile carefully and analyze to identify the questions the human student could not answer."
         "Based on these unanswered questions, you will create an initial lesson plan."
         "When the teachers_agent asks you to update the lesson plan,"
         "you will revise it according to the human student's interests,"
         "which the teachers_agent will provide to you."
         "After updating, you will share the revised lesson plan with the teachers_agent.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[ file_read_tool]
)
assessor_agent = Agent(
    role="you are an assessor with expertice in geometry"
         "You will generate separate questions for human student",
    goal="you are an expert on geometry"
         "You will generate separate  questions on Geometry related to the lessonplan provided by the lessonplanner_agent for human student"
         "based on the lessonplans  and from  preassessmentfile  find in {file_paths1}",
    backstory="you are an expert on geometry"
         "You will generate separate  questions on Geometry related to the lessonplan provided by the lessonplanner_agent for human student"
         "based on the lessonplans  and from  preassessmentfile  find in {file_paths1}",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[ file_read_tool]   
)
teachers_agent=Agent(
    role="You are a geometry teacher with a strong understanding of the subject."
         "First, you will greet the human student upon entering the class."
         "Then, you will carefully teach the student based on the initial lesson plan provided by the lessonplanner_agent."
         "During the lesson, you will ask questions from the topics you are covering."
         "The human student will respond to your questions."
         "If the human student answers correctly, you will proceed to the next topic in the lesson plan. If the student answers incorrectly, you will go over the same topic again in detail."
         "If the human student expresses difficulty when you ask questions, you will inquire about their interests."
         "The human student will then share their interests with you. Based on this information, you will request the lessonplanner_agent to update the lesson plan according to the student's interests."
         "Once the updated lesson plan is provided by the lessonplanner_agent, you will continue teaching according to the new plan."
         "Note that you will access the human student's responses using the ShepherdInputTool() and perform actions accordingly based on the student's replies.",
    goal="You are a geometry teacher with a strong understanding of the subject."
         "First, you will greet the human student upon entering the class."
         "Then, you will carefully teach the student based on the initial lesson plan provided by the lessonplanner_agent."
         "During the lesson, you will ask questions from the topics you are covering."
         "The human student will respond to your questions."
         "If the human student answers correctly, you will proceed to the next topic in the lesson plan. If the student answers incorrectly, you will go over the same topic again in detail."
         "If the human student expresses difficulty when you ask questions, you will inquire about their interests."
         "The human student will then share their interests with you. Based on this information, you will request the lessonplanner_agent to update the lesson plan according to the student's interests."
         "Once the updated lesson plan is provided by the lessonplanner_agent, you will continue teaching according to the new plan."
         "Note that you will access the human student's responses using the ShepherdInputTool() and perform actions accordingly based on the student's replies.",
             
    backstory="You are a geometry teacher with a strong understanding of the subject."
         "First, you will greet the human student upon entering the class."
         "Then, you will carefully teach the student based on the initial lesson plan provided by the lessonplanner_agent."
         "During the lesson, you will ask questions from the topics you are covering."
         "The human student will respond to your questions."
         "If the human student answers correctly, you will proceed to the next topic in the lesson plan. If the student answers incorrectly, you will go over the same topic again in detail."
         "If the human student expresses difficulty when you ask questions, you will inquire about their interests."
         "The human student will then share their interests with you. Based on this information, you will request the lessonplanner_agent to update the lesson plan according to the student's interests."
         "Once the updated lesson plan is provided by the lessonplanner_agent, you will continue teaching according to the new plan."
         "Note that you will access the human student's responses using the ShepherdInputTool() and perform actions accordingly based on the student's replies.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[ file_read_tool,shepherd_input_tool] 
)  
lessonplanner_docs_task= Task(
    description="You are a LessonPlanner_Agent with extensive knowledge in geometry."
         "You are given a preassessmentfile of a human student,which is find in the {file_paths1}"
         "you will read this preassessmentfile carefully and analyze to identify the questions the human student could not answer."
         "Based on these unanswered questions, you will create an initial lesson plan."
         "When the teachers_agent asks you to update the lesson plan,"
         "you will revise it according to the human student's interests,"
         "which the teachers_agent will provide to you."
         "After updating, you will share the revised lesson plan with the teachers_agent.",
    expected_output="You are a LessonPlanner_Agent with extensive knowledge in geometry."
         "You are given a preassessmentfile of a human student,which is find in the {file_paths1}"
         "you will read this preassessmentfile carefully and analyze to identify the questions the human student could not answer."
         "Based on these unanswered questions, you will create an initial lesson plan."
         "When the teachers_agent asks you to update the lesson plan,"
         "you will revise it according to the human student's interests,"
         "which the teachers_agent will provide to you."
         "After updating, you will share the revised lesson plan with the teachers_agent.",
    agent=lessonplanner_agent,
    llm = ChatOpenAI(temperature=0.75, model_name="gpt-4o"),
    step_callback=my_intermediate_step_callback
)
assessor_docs_task= Task(
    description="you are an expert on geometry"
         "You will generate separate  questions on Geometry related to the lessonplan provided by the lessonplanner_agent for human student"
         "based on the lessonplans  and from  preassessmentfile  find in {file_paths1}",
    expected_output="you are an expert on geometry"
         "You will generate separate  questions on Geometry related to the lessonplan provided by the lessonplanner_agent for human student"
         "based on the lessonplans  and from  preassessmentfile  find in {file_paths1}",
    agent=assessor_agent,
    llm = ChatOpenAI(temperature=0.75, model_name="gpt-4o"),
    step_callback=my_intermediate_step_callback
)
teachers_docs_task= Task(
    description="You are a geometry teacher with a strong understanding of the subject."
         "First, you will greet the human student upon entering the class."
         "Then, you will carefully teach the student based on the initial lesson plan provided by the lessonplanner_agent."
         "During the lesson, you will ask questions from the topics you are covering."
         "The human student will respond to your questions."
         "If the human student answers correctly, you will proceed to the next topic in the lesson plan. If the student answers incorrectly, you will go over the same topic again in detail."
         "If the human student expresses difficulty when you ask questions, you will inquire about their interests."
         "The human student will then share their interests with you. Based on this information, you will request the lessonplanner_agent to update the lesson plan according to the student's interests."
         "Once the updated lesson plan is provided by the lessonplanner_agent, you will continue teaching according to the new plan."
         "Note that you will access the human student's responses using the ShepherdInputTool() and perform actions accordingly based on the student's replies.",
    expected_output="You are a geometry teacher with a strong understanding of the subject."
         "First, you will greet the human student upon entering the class."
         "Then, you will carefully teach the student based on the initial lesson plan provided by the lessonplanner_agent."
         "During the lesson, you will ask questions from the topics you are covering."
         "The human student will respond to your questions."
         "If the human student answers correctly, you will proceed to the next topic in the lesson plan. If the student answers incorrectly, you will go over the same topic again in detail."
         "If the human student expresses difficulty when you ask questions, you will inquire about their interests."
         "The human student will then share their interests with you. Based on this information, you will request the lessonplanner_agent to update the lesson plan according to the student's interests."
         "Once the updated lesson plan is provided by the lessonplanner_agent, you will continue teaching according to the new plan."
         "Note that you will access the human student's responses using the ShepherdInputTool() and perform actions accordingly based on the student's replies.",
    agent=teachers_agent,
    llm = ChatOpenAI(temperature=0.75, model_name="gpt-4o"),
    step_callback=my_intermediate_step_callback
)
crew = Crew(
    agents=[lessonplanner_agent,assessor_agent,teachers_agent],
    tasks=[lessonplanner_docs_task,assessor_docs_task,teachers_docs_task],
    verbose=True
     
)
result=crew.kickoff(inputs={
    'file_paths1': '/home/shovan/Videos/shepherdpreassessment.txt'
})
st.write(result)