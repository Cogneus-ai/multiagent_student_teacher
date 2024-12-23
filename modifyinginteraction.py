import os
import openai
import dotenv
import time
import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
from crewai_tools import Tool
#from langchain.agents import  Tool
import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
from crewai_tools import Tool
#from langchain.agents import  Tool
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
import re
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
demo_ephemeral_chat_history = ChatMessageHistory()
# Session State Initialization
if "summary_chat_history" not in st.session_state:
    st.session_state["summary_chat_history"] = ChatMessageHistory()
if "interactions" not in st.session_state:
    st.session_state["interactions"] = 0
#if "result" not in st.session_state:
    #st.session_state["result"] = None
if "result_1" not in st.session_state:
    st.session_state["result_1"] = None

def summarize_messages():
    # Ensure summary_chat_history exists in session state
    if "summary_chat_history" not in st.session_state:
        st.session_state["summary_chat_history"] = ChatMessageHistory()

    # Access the stored chat history
    stored_messages = st.session_state["summary_chat_history"].messages

    # If no messages exist, return False
    if len(stored_messages) == 0:
        return False

    # Create a summarization prompt
    summarization_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "user",
                "Distill the above chat messages into a single summary message.",
            ),
        ]
    )

    # Build the summarization chain
    summarization_chain = summarization_prompt | llm

    # Generate the summary message
    summary_message = summarization_chain.invoke({"chat_history": stored_messages})

    # Clear ephemeral and session-based chat history
    st.session_state["summary_chat_history"].clear()

    # Update session state with the summarized message
    if "demo_ephemeral_chat_history" not in st.session_state:
        st.session_state["demo_ephemeral_chat_history"] = ChatMessageHistory()
    st.session_state["demo_ephemeral_chat_history"].add_message(summary_message)

    return True

dotenv.load_dotenv()
llm=ChatOpenAI(temperature=0, model_name="gpt-4o")

# Loading environment variables
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"

# Initializing tools


st.sidebar.title("Select Student")
students = {
    "shepherd": "/home/shovan/Videos/shepherdpreassessment.txt", 
    "ollie": "/path/to/b_preassessment.txt", 
    "lucy": "/path/to/c_preassessment.txt"
}

selected_student = st.sidebar.radio("Choose a Student:", list(students.keys()))

# Get the corresponding pre-assessment file for the selected student
preassessment_file = students.get(selected_student)

if preassessment_file and os.path.exists(preassessment_file):
    st.write(f"Selected pre-assessment file: {preassessment_file}")
else:
    st.error("Error: The selected student's pre-assessment file could not be found.")

# Initialize FileReadTool with the selected student's file
file_read_tool = FileReadTool(file_path=preassessment_file)
# Define agents

# LessonPlanner Agent
lessonplanner_agent = Agent(
    role="LessonPlanner_Agent",
    goal="Create an initiallesson plan to the topic where the humanstudent is weak",
    backstory="You have a good knowledge in geometry.you create an initiallessonplan where human student weak"
              "you provide this initial lessonplan to the assessor_agent and teachers_agent",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[file_read_tool]
)

# Assessor Agent
assessor_agent = Agent(
    role="Assessor_Agent",
    goal="Generate questions to assess the student's understanding based on the lesson plan.",
    backstory="You will create an assessment for the student based on the lesson plan provided by the lesson planner agent.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[file_read_tool]
)

# Teacher Agent
teachers_agent = Agent(
    role="Geometry Teacher_Agent",
    goal="Teach the student based on the initiallesson plan,after teaching you ask question to the human student",
    backstory="You will teach the human student based on the initial lesson plan provided by the lessonplanner_agent."
              "During the teaching session, you must ask questions from the topics you have already taught."
              "If the human student gives the correct answer, you will move on to another topic."
              "However, if the student cannot provide the correct answer, you will only explain only this topic  which the student was unable to answer"
              "and you are strictly forbidden from introducing any other topic. If the student shows confusion, you must ask the student about their interests."
              "You are an interactive teacher who follows the lesson plan and adapts based on the student's needs.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    #lesson_plan=lesson_plan,
    tools=[file_read_tool]
)

# Callback function for intermediate steps
def my_intermediate_step_callback(step_result):
    # You can log or handle intermediate results here
    print(f"Intermediate Step: {step_result}")

# Task Definitions

# LessonPlanner Agent
lessonplanner_agent = Agent(
    role="LessonPlanner_Agent",
    goal="Create an initiallesson plan to the topic where the humanstudent is weak",
    backstory="You have a good knowledge in geometry.you create an initiallessonplan where human student weak"
              "you provide this initial lessonplan to the assessor_agent and teachers_agent",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[file_read_tool]
)

# Assessor Agent
assessor_agent = Agent(
    role="Assessor_Agent",
    goal="Generate questions to assess the student's understanding based on the lesson plan.",
    backstory="You will create an assessment for the student based on the lesson plan provided by the lesson planner agent.",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[file_read_tool]
)

# Teacher Agent
teachers_agent = Agent(
    role="Interactive geometry Teacher_Agent who teaches human student of class nine",
    goal="You will teach each topic mentioned in the initial lesson plan one by one.After each conversation/explanation you will ask one question to the student to make sure they understood the discussion completely"
         "Whenever the student responds something it is mandatory to acknowledge it and say whether it is correct or not"
         "You are forbidden to discuss other topics without first acknowledging whether the student's answer is correct or not"
         "You will never cover all the topics of the lesson plan in a single interaction, and in one interaction, you will ask the human student only one question"
         "If the student correctly answers the question from the portion of the initial lesson plan you have taught, you will not teach that portion again",
    backstory="You will teach the human student based on the initial lesson plan provided by the lessonplanner_agent. "
              "After teaching  a topic you ask question to the human student to check that they have understood the topic taught"
              "During the teaching session, if the student answers a question correctly, confirm their understanding with "
              "'You answered correctly! Let's move on to the next topic.' and proceed to the next topic. "
              "If the student gives an incorrect answer, say 'That's not correct. Let me explain this topic again in a simpler way.' "
              "Reteach only the topic they got wrong without introducing new topics and also ask the student about their interests to adapt the teaching plan. "
              "If the student seems confused or expresses disinterest, ask them about their interests to adapt the teaching plan. "
              "Avoid repetitive greetings or irrelevant phrases during the session. "
              "Your task is to assess the student's understanding dynamically and adjust teaching strategies accordingly."
              "Whenever you ask a question and the student responds something it is mandatory to acknowledge it and carefully check it and say whether it is correct or not "
              "for example if the answer is correct you write'Hello Again! It seems you have correctly answered the question! Let us discuss further based on your understanding'"
              "if the student is unable to answer at all or expresses disinterest you write'it seems you are having problem with this question,"
              "can you please let me know about your interest and learning preferences so that I can incorporate it in my teaching and make it more interesting for you'"
              "MAKE SURE THAT YOU MUST COMPLETE TEACHING EACH TOPIC MENTIONED IN THE initial lesson plan Which lessonplan is provided by lessonplanner_agent .ALSO ASSESS THAT THE STUDENT HAS UNDERSTAND EACH TOPIC OF THE initial lesson plan",
    allow_delegation=False,
    verbose=True,
    memory=True,
    tools=[file_read_tool]
)

# Callback function for intermediate steps
def my_intermediate_step_callback(step_result):
    # You can log or handle intermediate results here
    print(f"Intermediate Step: {step_result}")

# Task Definitions

# LessonPlanner Task
lessonplanner_docs_task = Task(
    description="You have a good knowledge in geometry.you create an initiallessonplan where human student weak"
                 "you provide this initial lessonplan to the assessor_agent and teachers_agent",
    expected_output="You have a good knowledge in geometry.you create an initiallessonplan where human student weak"
                     "you provide this initial lessonplan to the assessor_agent and teachers_agent",
    agent=lessonplanner_agent,
    llm=ChatOpenAI(temperature=0.75, model_name="gpt-4o"),
    step_callback=my_intermediate_step_callback
)

# Assessor Task
assessor_docs_task = Task(
    description="The Assessor_Agent generates questions based on the lesson plan created by the lessonplanner agent.",
    expected_output="A set of assessment questions to evaluate the student's understanding of geometry, specifically on triangles.",
    agent=assessor_agent,
    llm=ChatOpenAI(temperature=0.75, model_name="gpt-4o"),
    step_callback=my_intermediate_step_callback
)

# Teacher Task
teachers_docs_task = Task(
    description="You are an interactive Socratic geometry teacher responsible for teaching a student interactively based on the lesson plan. "
        "You will teach each topic mentioned in the initial lesson plan one by one.After each conversation/explanation you will ask one question to the student to make sure they understood the discussion completely"
        "Start with a friendly introduction only during the first interaction. As the session progresses, avoid unnecessary greetings. "
        "Your teaching must adapt based on the student's responses."
        "You will never cover all the topics of the lesson plan in a single interaction, and in one interaction, you will ask the human student only one question"
        "Your primary task is to evaluate the student's response correctly "
        "immediately after they answer your question."
        "If the student correctly answers the question from the portion of the initial lesson plan you have taught, you will not teach that portion again"
        "If the student's answer is correct, confirm it by saying: 'You answered correctly! Let's move on to the next topic.' "
        "If the answer is incorrect, say: 'That's not correct. Let me explain this topic again,' and reteach the same topic in simpler terms.Also, ask for the student's interests and Learning prefence (Visual,audio, kinesthetic etc) "
        "During the first interaction, start by introducing the topic and asking a question. "
        "Do not skip this evaluation step at any point in the session. Ensure all responses remain correct, clear, concise, and aligned with the lesson plan."
        "You are forbidden to discuss other topics without first acknowledging correctly whether the student's answer is correct or not",
    expected_output= "A dynamic, interactive teaching session where the teacher uses student feedback to adapt teaching strategies. "
                     "You will teach each topic mentioned in the initial lesson plan one by one.After each conversation/explanation you will ask one question to the student to make sure they understood the discussion completely"
                     "You will first evaluate correctly the student's response before proceeding to next topic"
                     "After teaching  a topic you ask question to the human student to check that they have understood the topic taught"
                     "Correct answers should lead to confirmation and progression to the next topic, while incorrect answers should prompt reteaching of the current topic and asking about the student's interests and learning preference. "
                     "Engagement with the student must remain interactive, encouraging, and based solely on the lesson plan."
                     "The teacher has to correctly and carefully evaluate the student's response and declare it as correct or incorrect and immediately adapt the teaching "
                     "strategy, either reteaching or moving to the next topic. During the first interaction, the teacher "
                     "introduces the lesson plan and ensures immediate and correct evaluation of the student's response."
                     "During the first interaction, the teacher introduces the lesson plan, evaluates the first student response explicitly, and ensures dynamic engagement "
                     "throughout the session."
                     "Whenever you ask a question and the student responds something it is mandatory to acknowledge it check it carefully for correctness and say whether it is correct or not "
                     "for example if the answer is correct you write'Hello Again! It seems you have correctly answered the question! Let us discuss further based on your understanding'"
                     "If the student gives an incorrect answer, say 'That's not correct. Let me explain this topic again in a simpler way.' "
                     "Reteach only the topic they got wrong without introducing new topics.Also, ask about the student's interests and learning preference "
                     "if student is unable to answer at all or expresses disinterest you write'it seems you are having problem with this question,"
                     "can you please let me know about your interest and learning preferences so that i can incorporate it in my teaching and make it more interesting for you'"
                     "When the student responds with 'I don't know' you will describe the topic with easier examples and ask about the student's interests and learning preference "
                     "MAKE SURE THAT YOU MUST COMPLETE TEACHING EACH TOPIC MENTIONED IN THE initial lesson plan.ALSO ASSESS THAT THE STUDENT HAS UNDERSTAND EACH TOPIC OF THE initial lesson plan"
                     "You are strictly forbidden to act outside the instructions given in the prompt. You must work exactly as instructed in the prompt and not do anything beyond it.",
    agent=teachers_agent,
    #human_input=True,
    llm=ChatOpenAI(temperature=0.75, model_name="gpt-4o"),
    step_callback=my_intermediate_step_callback
)

# Crew Definition
crew = Crew(
    agents=[lessonplanner_agent, assessor_agent, teachers_agent],
    tasks=[lessonplanner_docs_task, assessor_docs_task, teachers_docs_task],
    callbacks=[my_intermediate_step_callback],
    verbose=True
)
# Display Results for First Crew
if "result" not in st.session_state:
    st.session_state["result"] = crew.kickoff()

st.write("### First Crew Result:")
st.write(st.session_state["result"])
# Process First Crew Result
if hasattr(st.session_state["result"], 'raw'):  # Check if result has the 'raw' attribute
    raw_content = st.session_state["result"].raw  # Extract the raw string

    # Split the string to isolate the "Teacher" part
    if raw_content.startswith("Teacher:"):
        result = raw_content.split("Teacher:", 1)[1].strip()  # Remove "Teacher:" and leading spaces
    else:
        result = raw_content  # Fallback if no "Teacher:" prefix found

    # Add the teacher's response to the summary chat history
    st.session_state["summary_chat_history"].add_ai_message(result)
#summarize_messages()
#Finale_summary=demo_ephemeral_chat_history.messages
#Finale_summary=summary_chat_history.messages[0].content
#summary_chat_history.clear()


# Variable to store lesson plan manually
lesson_plan = []



# LessonPlanner Agent
lessonplanner_agent_1 = Agent(
    role="LessonPlanner_Agent",
    goal="Create an updated lesson plan based on the student's interest which is provided by teachers_agent_1 to help the student understand geometry topics.",
    backstory="You are a skilled lesson planner who creates detailed updated lesson plans based on the student feedback."
              "You will gather the human student's interests from the teachers_agent and use that information to update the initial lesson plan based on lesson plan initial_lesson_plan. Then, you will provide the updated lesson plan to teachers_agent_1."
               "When teachers_agent_1 asks you to update the lesson plan, you must update the lesson plan."
               "Once the lesson plan has been updated based on the student's interests, it will not be updated again unless the student mentions ay additional interests or learning preferences",
    allow_delegation=False,
    verbose=True,
    
)

# Assessor Agent
assessor_agent_1= Agent(
    role="Assessor_Agent",
    goal="Generate questions to assess the student's understanding based on the lesson plan.",
    backstory="You will create an assessment for the student based on the lesson plan provided by the lesson planner agent.",
    allow_delegation=False,
    verbose=True,
    
)

# Teacher Agent
teachers_agent_1 = Agent(
    role="Interactive Teacher_Agent",
    goal="you have a good knowledge in geometry.you teach the student based on the initial lesson plan, ask questions, and provide explanations when needed."
         "You will explain each topic of the initial lesson plan one by one."
         "Whenever you ask a question and the student responds something it is mandatory to evaluate it carefully and correctly, acknowledge it, and say whether it is correct or not "
         "Please make sure that you properly evaluate each answer given by the student and respond appropriately based on whether it is correct or incorrect"
         "If the student correctly answers the question from the portion of the  lesson plan you have taught, you will not teach that portion again"
         "for example if the answer is correct you write'Hello Again! It seems you have correctly answered the question! Let us discuss further based on your understanding'"
         "if student is unable to answer at all or expresses disinterest you write'it seems you are having problem with this question,"
         "can you please let me know about your interest and learning preferences so that i can incorporate it in my teaching and make it more interesting for you'"
         "You will never cover all the topics of the lesson plan in a single interaction, and in one interaction, you will ask the human student only one question"
         "After the initial lesson plan is updated by lessonplanner_agent_1, you will explain each portion of the initial and  lesson plan based on the student's interests"
         "However, the initial lesson plan and updated lesson plan will never be explicitly presented to the Human student"
         "Until the lesson plan is updated, teaching will proceed according to the initial lesson plan, and once the lesson plan is updated, teaching will follow the updated lesson plan but cover each topic of the initial lesson plan. "
         "You can never display the lesson Plan to the student"
         "When the lesson Plan is updated  do as follows"
         "Use the updated  lesson Plan but describe one topic only from this lesson plan in your own words and ask one question to make sure that the student understands it"
         "You will teach the topics of the updated lesson Plan one by one in separate interactions with the Human student. Make sure the student understands each topic by questioning them and evaluating their answers"
         "You will not update the Lesson Plan once it has already been updated and no new interest is reported by the student",
    backstory="You are an interactive geometry teacher who follows the lesson plan and adapts based on the student's needs."
               "You will explain each topic of the initial lesson plan one by one."
              "when human student says their interest then you must suggest to the lessonplanner_agent_1 to update the lessonplan based on the student's interest"
              "Whenever you ask a question and the student responds something it is mandatory to evaluate it carefully and correctly, acknowledge it and say whether it is correct or not "
              "for example if the answer is CORRECT YOU MUST WRITE'Hello Again! It seems you have correctly answered the question! Let us discuss further based on your understanding'"
              "If the student gives an incorrect answer, say 'That's not correct. Let me explain this topic again in a simpler way.''Also, please let me know about your interests and learning preference' "
              "Reteach only the topic they got wrong without introducing new topics. "
              "IF STUDENT write 'i don't know' YOU MUST WRITE 'That's not a problem' AND THEN EXPLAIN THAT TOPIC AGAIN and ask for their interests and learning preference"
              "if student is unable to answer at all or expresses disinterest you write'it seems you are having problem with this question,"
              "can you please let me know about your interest and learning preferences so that i can incorporate it in my teaching and make it more interesting for you'"
              "When the lesson Plan is updated  do as follows"
              "Use the updated  lesson Plan but describe one topic only from this lesson plan in your own words and ask one question to make sure that the student understands it"
              "You will teach the topics of the updated lesson Plan one by one in separate interactions with the Human student. Make sure the student understands each topic by questioning them and evaluating their answers"
              "You will not update the Lesson Plan once it has already been updated and no new interest is reported by the student",
              
    allow_delegation=True,
    verbose=True,
    #memory=True
)
# Task Definitions
lessonplanner_docs_task_1= Task(
    description="when teachers_agent_1 suggest you to update lessonplan,then you must update lessonplan based on the student's interest"
                "You will update only those portions of the initial lesson plan based on initial_lesson_plan that are included based on the student's interests"
                "Once the lesson plan has been updated based on the student's interests, it will not be updated again unless the student mentions their new interests",
    expected_output="You are a skilled lesson planner who creates detailed updated lesson plans based on the student feedback."
              "You will gather the human student's interests from the teachers_agent and use that information to update the initial lesson plan created by the lessonplanner_agent. Then, you will provide the updated lesson plan to teachers_agent_1."
               "When teachers_agent_1 asks you to update the lesson plan, you must update the lesson plan.",
    agent=lessonplanner_agent_1,
    llm=ChatOpenAI(temperature=0.75, model_name="gpt-4o"),
)

# Teacher Task
teachers_docs_task_1= Task(
    description="A dynamic, interactive teaching session where the teacher uses analogies and personalized teaching methods based on the student's responses."
                    "You will teach each topic mentioned in the initial lesson plan one by one based on lessonplan initial_lesson_plan.After each conversation/explaination on one topic you will ask one question to the student to make sure they understood the discussion completely"
                    "You will teach each topic of the initial lesson plan in separate interactions, covering one topic per interaction, provided the student gives correct answers"
                    "Do not repeat any topic that the student has already answered correctly"
                    "you are forbidden to teach more than one topic in one explanation or conversation."
                    "you will wait for the answer of the student before asking the next question"
                    "Please make sure that you properly evaluate each answer given by the student and respond appropriately based on whether it is correct or incorrect"
                    "Keep your interaction brief and focused on a topic with only one question at the end to evaluate Student's understanding"
                    "you will interact with the human student, starting with a greeting and an introduction to the lesson. Based on the previous chat history {Previous_chat_summary} and student's answers or feedback {feedback}, if the student shows confusion, you will ask about their interests to adjust the lesson plan accordingly. If student said about their interest then must ordered to the lessonplanner_agent_1 to update the lessonplan."
                    "Begin each session with a greeting and introduce the lesson."
                    "Teach one topic at a time from the initial or updated lesson plan."
                    "After explaining a topic, ask one question to assess the studentâ€™s understanding."
                    "Wait for the student's answer before proceeding."
                    "Evaluate each answer thoroughly:"
                    "If correct: Respond, 'You answered correctly! Let's move on to the next topic,' and teach the next topic."
                    "If incorrect: Respond, 'That's not correct. Let me explain this topic again in a simpler way,' and reteach the same topic."
                    "If the student says, 'I don't know,' respond, 'That's not a problem,' and reteach the topic."
                    "Adapt your teaching based on the student's responses and feedback."
                    "If the student seems confused, ask about their learning preferences and adjust the lesson plan accordingly via lessonplanner_agent_1."
                    "When the lesson plan is updated:"
                    "Use the updated lesson plan but never mention it explicitly"
                    "Teach each topic individually, ensuring full understanding before moving on"
                    "After the lesson plan is updated, teach one topic at a time from the updated lesson plan and asked a single question to the student whether the topic was understood"
                    "if the student answers the question correctly then do not teach the same topic but proceed to the next topic in the lesson plan. If the student answers incorrectly then explain the topic in a simpler way"
                    "After the lesson plan is updated:"
                    "Do not teach the updated lesson plan verbatim"
                    "Rephrase each portion of the updated lesson plan into simpler, laymanâ€™s terms, tailored to the studentâ€™s interests and learning style"
                    "Never show or mention the updated lesson plan explicitly to the student"
                    "Adapt teaching only after confirming the studentâ€™s understanding of the current topic"
                    "Update the lesson plan only when new interests are shared"
                    "Do not update the lesson plan again unless the student shares new interests"
                    "Avoid covering multiple topics in a single interaction"
                    "Answer the student's specific questions in a Socratic manner, guiding them to find answers without introducing unrelated topics"
                    "Ensure all topics in the lesson plan are taught and understood through focused, concise interactions"
                    "Evaluate every response and proceed only after confirming understanding"
                    "Until the lesson plan is updated, teaching will proceed according to the initial lesson plan, and once the lesson plan is updated, teaching will follow the updated lesson plan.",
    expected_output="A dynamic, interactive teaching session where the teacher uses analogies and personalized teaching methods based on the student's responses."
                    "Teach one topic at a time based on the lesson plan (initial or updated)"
                    "Assess understanding with one question after each explanation"
                    "Evaluate the studentâ€™s answer carefully and respond:"
                    "Correct: 'You answered correctly! Let's move to the next topic.'"
                    "Incorrect: 'That's not correct. Let me explain it again in a simpler way.'"
                    "Unsure ('I don't know'): 'That's not a problem. Let me explain it again.'"
                    "Adapt teaching based on responses, learning preferences, or interests."
                    "After the lesson plan is updated, teach one topic at a time from the updated lesson plan"
                    "Explanation of one portion of the updated lesson plan in layman's terms."
                    "One question to check student understanding"
                    "Evaluation of the student's answer to determine next steps"
                    "After each explanation, ask one question to ensure the student understands the topic"
                    "Wait for the student's response, evaluate it thoroughly, and proceed based on the answer:"
                    "Correct: Move to the next topic."
                    "Incorrect:Mention that the answer is not correct and then reteach the same topic in a simpler way"
                    "Adapt teaching only after confirming the studentâ€™s understanding of the current topic"
                    "Update the lesson plan only when new interests are shared"
                    "Complete all topics in the lesson plan while ensuring full understanding"
                    "MAKE SURE THAT YOU COMPLETE TEACHING EACH TOPIC MENTIONED IN THE initial lesson plan .ALSO ASSESS THAT THE STUDENT HAS UNDERSTAND EACH TOPIC OF THE initial lesson plan"
                    "You are strictly forbidden to act outside the instructions given in the prompt. You must work exactly as instructed in the prompt and not do anything beyond it.",
    agent=teachers_agent_1,
    llm=ChatOpenAI(temperature=0.75, model_name="gpt-4o"),
)
my_crew = Crew(
    agents=[lessonplanner_agent_1, assessor_agent_1, teachers_agent_1],
    tasks=[teachers_docs_task_1],
    memory=True,
    verbose=True,
)


# Input and Display Logic for Student Interactions
interaction_id = st.session_state["interactions"]

# Create a dynamic input box and submit button for the current interaction
student_response = st.text_input(
    f"Student's Input for Interaction {interaction_id + 1}:",
    key=f"student_input_{interaction_id}"
)

# Submit Button for the Current Interaction
if st.button(f"Submit Interaction {interaction_id + 1}", key=f"submit_button_{interaction_id}"):
    if student_response.strip():
        # Add student's input to chat history
        st.session_state["summary_chat_history"].add_user_message(student_response)

        # Process the input with the Crew
        st.session_state["result_1"] = my_crew.kickoff(
            inputs={
                "feedback": student_response,
                "Previous_chat_summary": [
                    msg.content for msg in st.session_state["summary_chat_history"].messages
                ],
            }
        )

        # Extract and display the Teacher's response
        if hasattr(st.session_state["result_1"], "raw"):
            raw_content = st.session_state["result_1"].raw

            # Extract the Teacher's response
            if raw_content.startswith("Teacher:"):
                result_1 = raw_content.split("Teacher:", 1)[1].strip()
            else:
                result_1 = raw_content

            # Add teacher's response to chat history
            st.session_state["summary_chat_history"].add_ai_message(result_1)

            # Display the teacher's response
            st.write(f"### Teacher's Response for Interaction {interaction_id + 1}:")
            st.write(result_1)

        # Increment the interaction count
        st.session_state["interactions"] += 1

# Check for Maximum Interactions
if st.session_state["interactions"] >= 10:
    st.write("### Maximum interactions reached. Session ended.")
    st.stop()


