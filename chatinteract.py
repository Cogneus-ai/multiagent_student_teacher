from langgraph.graph.state import StateGraph
from langgraph.prebuilt import ToolNode

# Define the action functions for each node
def lesson_planner_action(state):
    student_input = state.get("student_input", "")
    return {"lesson_plan": f"Created lesson plan based on: {student_input}"}

def teacher_action(state):
    lesson_plan = state.get("lesson_plan", "")
    return {"feedback": f"Taught lesson: {lesson_plan}"}

def assessor_action(state):
    feedback = state.get("feedback", "")
    return {"assessment": f"Assessed feedback: {feedback}"}

# Initialize ToolNodes with the action functions
lesson_planner_node = ToolNode(
    name="LessonPlannerNode",
    action=lesson_planner_action
)

teacher_node = ToolNode(
    name="TeacherNode",
    action=teacher_action
)

assessor_node = ToolNode(
    name="AssessorNode",
    action=assessor_action
)

# Define the state schema for the graph
state_schema = {
    "student_input": str,
    "lesson_plan": str,
    "feedback": str,
    "assessment": str,
}

# Create the graph
graph = StateGraph(state_schema=state_schema)

# Add nodes to the graph
graph.add_node("LessonPlannerNode", lesson_planner_node)
graph.add_node("TeacherNode", teacher_node)
graph.add_node("AssessorNode", assessor_node)

# Define transitions between nodes
graph.add_edge("LessonPlannerNode", "TeacherNode", transfer_state={"lesson_plan": "output"})
graph.add_edge("TeacherNode", "AssessorNode", transfer_state={"feedback": "output"})

# Simulate the process with initial state
initial_state = {"student_input": "Geometry pre-assessment data"}
final_state = graph.run(initial_state)

print(final_state)
