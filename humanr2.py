import os
from crewai import Agent, Task, Crew, Process
from crewai.flow.flow import Flow
from crewai_tools import FileReadTool
import dotenv
# Load environment variables
dotenv.load_dotenv()
# Tool for reading preassessment files
file_read_tool = FileReadTool()
# Shepherd Input Tool for human interaction
class ShepherdInputTool(Tool):
    def __init__(self):
        super().__init__(
            name="Shepherd Input Tool",
            description="Tool for collecting input from Shepherd (human student).",
            func=self.get_shepherd_input
        )

    def get_shepherd_input(self, message: str = "Please provide input:", **kwargs):
        unique_key = f"shepherd_input_{time.time()}"
        return st.text_input(message, key=unique_key)

# Initialize tools
shepherd_input_tool = ShepherdInputTool()

# Lesson Planner Agent
lesson_planner = Agent(
    role="Lesson Planner",
    goal="Analyze the preassessment file and create a lesson plan focusing on weak areas in Geometry.",
    backstory="An expert in educational planning, adept at identifying and addressing learning gaps.",
    memory=True,
    verbose=True,
    tools=[file_read_tool]
)

# Assessor Agent
assessor = Agent(
    role="Assessor",
    goal="Design an assessment plan based on the provided lesson plan.",
    backstory="Ensures assessments align with the lesson objectives and effectively evaluate student learning.",
    memory=True,
    verbose=True
)

# Teacher Agent
teacher = Agent(
    role="Teacher",
    goal="Teach lessons interactively based on the lesson plan, "
         "assess student responses, and adapt the teaching approach as needed.",
    backstory="A passionate educator skilled at engaging students and addressing their learning needs."
               "Use this tool to continuously interact with the human student, understand their problems,"
               "find out what they are interested in so that you can teach all the topics provided in the lesson plan"
               "in such a way that the student understands them. Assess their understanding using the assessment plan given by the assessor agent",
    memory=True,
    tools=[shepherd_input_tool],
    verbose=True
)

# Tasks for Lesson Planner
lesson_planning_task = Task(
    description=(
        "Read the preassessment file located at {preassessment_file}. "
        "Parse the content to extract questions and student responses. "
        "Identify weak areas in Geometry based on incorrect answers, and create an initial lesson plan focused on these topics."
    ),
    expected_output="An initial lesson plan addressing weak areas identified in {preassessment_file}.",
    agent=lesson_planner,
    tools=[file_read_tool]
)

# Tasks for Assessor
assessment_task = Task(
    description="Create an assessment plan based on the initial lesson plan.",
    expected_output="A set of assessment questions with grading criteria based on the initial lesson plan.",
    agent=assessor
)

# Tasks for Teacher
teaching_task = Task(
    description=(
        "Greet the student and teach according to the initial lesson plan. For each topic:\n"
        "1. Ask questions based on the topic.\n"
        "2. If the student answers correctly, proceed to the next topic.\n"
        "3. If the student answers incorrectly, repeat the topic.\n"
        "4. If the student says 'I find difficulty', inquire about their interests and inform the Lesson Planner Agent to update the lesson plan accordingly."
    ),
    expected_output=(
        "Interactive teaching session addressing student responses, with topics "
        "adjusted as needed based on student performance and interests."
    ),
    agent=teacher,
    human_input=True
)

# Define the crews
crew1 = Crew(
    agents=[lesson_planner, assessor],
    tasks=[lesson_planning_task, assessment_task],
    process=Process.sequential
)

crew2 = Crew(
    agents=[teacher],
    tasks=[teaching_task],
    process=Process.sequential
)

# Define the flow
flow = Flow(
    crews=[crew1, crew2],
    inputs={"preassessment_file": "/home/shovan/Videos/shepherdpreassessment.txt"}
)

# Kickoff the flow
result = flow.kickoff()
print(result)