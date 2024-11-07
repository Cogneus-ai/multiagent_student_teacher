##importing necessary modules
import os
import re
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
##loading environmentfile
dotenv.load_dotenv()
def my_intermediate_step_callback(agent, task, step_info):
    print(f"Step reached in task: {task.description}, Agent: {agent.role}, Step info: {step_info}")
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"
file_read_tool = FileReadTool()
file_paths1 = [
     '/home/shovan/Videos/shepherdpreassessment.txt',
]
##agents are define one by one
lessonplanner_agent = Agent(
    role="You are a LessonPlanner_Agent with extensive knowledge in geometry.who can provide appropriate lessonplan for student of class 9,whose preassessmentfile is present in {file_paths1} on triangles and their different types and theorem",
    goal="You have to provide initial lessonlan based on the topics not understood by the student as can be seen from the preassessmentfile found in {file_paths1}."
         "you will modify this lessonplan based on the request of a tecahers_agent as needed to match the student's requirements",
    backstory= "You are a LessonPlanner_Agent with extensive knowledge in geometry."
         "You are given a preassessmentfile of a human student,which is found in the {file_paths1}"
         "you will read this preassessmentfile carefully and analyze to identify the questions the human student could not answer."
         "Based on these unanswered questions, you will create an initial lessonplan"
         "When the teachers_agent asks you to update the lesson plan,"
         "you will revise it according to the human student's interests and his/her difficulties in understanding the lesson being taught,"
         "After updating, you will share the revised lesson plan with the teachers_agent and assessor_agent.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[ file_read_tool]
)
assessor_agent = Agent(
    role="you are an assessor with expertize in geometry who generates appropriate questions for student in class 9 on triangles and their different types and theorem based on lessonplan created by the lessonplanner_agent"
         "You will modify initial assessment questions based on changed lessonplan everytime it is changed by the lessonplanner_agent",
    goal="to create assessment plan that a perfect to assess the student progress based on lessonplan as created by the lessonplanner_agent on triangles its types and theorem for class 9",     
    backstory="you are an expert on geometry"
         "Your initial assessment plan covers topics that the student was unable to understand as shown in the preassessmentfile in {file_paths1}"
         "you will modify the assessment plan when the lessonplan changes so that the student can be properly assessed on the topics included in it"
         "you will send the assessment plan you create to the teachers_agent for its use",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[file_read_tool]   
)
teachers_agent = Agent(
    role="Interactive Geometry Teacher who uses the lessonplan and assessmentplan provided by the lessonplanner_agent and the assessor_agent respectively to interact with the human student and teach them about triangles its types and theorem for class 9",
    goal="Teach geometry interactively,adapting to human student's interests and comprehension levels, using analogies when needed.",
    backstory="A compassionate teacher who adjusts lesson delivery based on student responses, particularly about triangles their types and theorems for class 9."
              "you will start with a greeting and start teaching based on the lessonplan and assessment plan given by the lessonplanner_agent and assessor_agent"
              "you will check that the student understand what you are teaching and clarify topics that student failed to understand"
              "You will give primary importance to the student's inputs and respond to their doubts and then proceed with remainder part of the lesson"
              "When the student has difficulty in understanding find out about their other interests and learning preferences so that you can teach appropriately"
              "then you will Ask the lessonplanner_agent and assessor_agent to modify lessonplan and assessmentplan as required to ensure that the student is able to make progress and understand the lesson"
              "Always pay careful attention to the student's input and modify your teaching according to the student's reading ability and interest in the subject",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[ file_read_tool] 
)  
##tasks of agents are define one by one
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
    description= "Start the class with a greeting and describe the goal of lesson"
        "Engage human student by asking him to share what he knows. If he shows confusion, prompt him to share an interest (e.g., music, animals, or any other topic) with ShepherdInputTool. "
        "Once an interest is provided, request an update from LessonPlanner_Agent to revise the lesson plan using this interest. "
        "After receiving the updated plan, proceed with teaching using analogies specific to Shepherd’s interest to make geometry concepts clearer. Remember that you do not need to repeat the greeting every time you engage with the student till the session is complete.",
    expected_output="A responsive interactive lesson with explanations using analogies based on Shepherd’s interest, whatever that may be."
                    "You will give primary importance to the student's inputs and respond to their doubts and then proceed with remainder part of the lesson",   
    agent=teachers_agent,
    human_input=True,
    llm = ChatOpenAI(temperature=0.75,model_name="gpt-4o"),
    step_callback=my_intermediate_step_callback
)
## crew is start action
crew = Crew(
    agents=[lessonplanner_agent,assessor_agent,teachers_agent],
    tasks=[lessonplanner_docs_task,assessor_docs_task,teachers_docs_task],
    callbacks=[my_intermediate_step_callback],
    verbose=True
)
class InteractionManager:
    def __init__(self, crew, max_interactions=10, passing_score=85):
        self.crew = crew
        self.max_interactions = max_interactions
        self.passing_score = passing_score
        self.interactions = 0
        self.assessment_score = 0

    def update_assessment_score(self, score):
        self.assessment_score = score
        print(f"Updated assessment score: {score}")
    
    def increment_interaction(self):
        self.interactions += 1
        print(f"Interaction count: {self.interactions}")

    def should_continue(self):
        # Check if maximum interactions reached or passing score achieved
        if self.interactions >= self.max_interactions:
            print("Maximum interactions reached.")
            return False
        if self.assessment_score >= self.passing_score:
            print("Student has passed the assessment.")
            return False
        return True

# Initiating the interaction manager with Crew AI system
interaction_manager = InteractionManager(crew)

# Start the loop for continuous interaction
while interaction_manager.should_continue():
    # Kick off the interaction with the student and teacher agent
    result = crew.kickoff(inputs={'file_paths1': '/home/shovan/Videos/shepherdpreassessment.txt'})
    
    # Debug print to see what the result looks like
    print("Result:", result)  # Check the content of the result
    
    # Check if result is a string and contains "assessment_score"
    if isinstance(result, str):
        # Example: If result is a long string, you need to extract the score using regex or string manipulation
        # For instance, if the result has a pattern "assessment_score: 72", you could try:
        score_match = re.search(r"assessment_score\s*[:]\s*(\d+)", result)
        if score_match:
            updated_score = int(score_match.group(1))  # Extract score from the matched group
        else:
            updated_score = 0  # Default score if not found
    else:
        # If it's already a dictionary, extract the score as before
        updated_score = result.get('assessment_score', 0)
    
    # Update the assessment score
    interaction_manager.update_assessment_score(updated_score)
    
    # Increment interaction count
    interaction_manager.increment_interaction()

    # Check if the loop should continue
    if not interaction_manager.should_continue():
        break

print("Lesson completed.")