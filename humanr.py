import os
from crewai import Agent, Task, Crew, Process
from crewai.flow.flow import Flow
from crewai_tools import FileReadTool
import dotenv
# Load environment variables
dotenv.load_dotenv()
# Tool for reading preassessment files
file_read_tool = FileReadTool()




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
    goal="Design an assessment plan to evaluate understanding of the lesson plan.",
    backstory="A meticulous evaluator who ensures assessments align with the learning objectives.",
    memory=True,
    verbose=True
)

# Teacher Agent
teacher = Agent(
    role="Teacher",
    goal=(
        "Teach lessons interactively, assess student responses, and adapt the teaching approach "
        "based on performance and interests."
    ),
    backstory="A passionate educator skilled at engaging students and addressing their learning needs.",
    memory=True,
    verbose=True
)

# Task for Lesson Planner to read and analyze the preassessment file
lesson_planning_task = Task(
    description=(
        "Read the preassessment file at {preassessment_file}. Identify questions where the student struggled "
        "and create an initial lesson plan focused on those topics in Geometry."
    ),
    expected_output="A lesson plan focusing on weak areas identified from {preassessment_file}.",
    agent=lesson_planner,
    tools=[file_read_tool]
)

# Task for Assessor to create an assessment plan
assessment_task = Task(
    description="Design an assessment plan based on the initial lesson plan.",
    expected_output="An assessment plan aligned with the lesson plan.",
    agent=assessor
)

# Task for Teacher to interact with the student
teaching_task = Task(
    description=(
        "Use the lesson plan to teach interactively. For each topic:\n"
        "1. Ask the student questions based on the topic.\n"
        "2. If the student answers correctly, proceed to the next topic.\n"
        "3. If the student answers incorrectly, repeat the explanation for the topic.\n"
        "4. If the student says 'I find difficulty', ask about their interests and request a lesson plan update "
        "from the Lesson Planner Agent."
    ),
    expected_output="Interactive teaching session addressing student responses and adjusting the plan as needed.",
    agent=teacher
)

# Define Crew 1 (Lesson Planner and Assessor)
crew1 = Crew(
    agents=[lesson_planner, assessor],
    tasks=[lesson_planning_task, assessment_task],
    process=Process.sequential
)

# Define Crew 2 (Teacher)
crew2 = Crew(
    agents=[teacher],
    tasks=[teaching_task],
    process=Process.sequential
)

# Human student interaction function (simulation)
def human_student_input(question):
    # Simulating a student's answer. In a real application, this would be input from the student.
    print(f"Question: {question}")
    return input("Your answer: ")  # Human input for student's answer

# Manual orchestration of the crews
def orchestrate():
    # Step 1: Execute Crew 1
    print("Executing Crew 1: Lesson Planner and Assessor")
    result_crew1 = crew1.kickoff(inputs={"preassessment_file": "/home/shovan/Videos/shepherdpreassessment.txt"})
    print("Crew 1 Result:", result_crew1)  # Print the result to inspect its structure

    # Access the output data based on structure
    lesson_plan = result_crew1.data  # Assuming 'data' is where the lesson plan is stored

    # Step 2: Execute Crew 2 - Teacher (Interacting with Human Student)
    print("Executing Crew 2: Teacher")
    
    # Loop through the topics in the lesson plan and interact with the student
    for topic in lesson_plan.get("topics", []):
        print(f"Teaching topic: {topic['name']}")
        # Ask a question related to the topic
        question = topic['question']
        student_answer = human_student_input(question)
        
        # Teacher evaluates the student's response
        if student_answer.lower() == topic['correct_answer'].lower():
            print("Correct answer! Proceeding to next topic.")
        else:
            print("Incorrect answer. Let's review this topic again.")
        
        # If student says "I find difficulty", ask about interests
        if "difficulty" in student_answer.lower():
            print("Teacher: I see you're having difficulty. What are your interests?")
            student_interests = input("Student interests: ")
            print(f"Teacher updates the lesson plan based on interests: {student_interests}")
            # Update lesson plan based on interests (can be expanded as needed)
            lesson_plan = {"topics": [{"name": "Adjusted Topic", "question": "Updated question", "correct_answer": "Updated answer"}]}
    
    print("Lesson completed.")

# Run the orchestration
orchestrate()