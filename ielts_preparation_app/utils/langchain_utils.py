from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish
from langchain.memory import ConversationBufferMemory
from typing import List, Union, Any
import re
import json
from .common import get_openai_response

# Инструменты для агента
class WritingAnalysisTool(BaseTool):
    name: str = "Writing Analysis"
    description: str = "Use this tool to analyze IELTS writing tasks"

    def _run(self, essay: str) -> str:
        # Здесь мы можем использовать нашу существующую логику анализа эссе
        # или создать новую с использованием LangChain
        # Для примера, вернем заглушку
        return "Analysis of the essay: Good structure, needs improvement in vocabulary."

class ReadingAnalysisTool(BaseTool):
    name: str = "Reading Analysis"
    description: str = "Use this tool to analyze IELTS reading responses"

    def _run(self, answers: str) -> str:
        # Заглушка для анализа ответов на чтение
        return "Reading analysis: 7 out of 10 correct answers."

class ListeningAnalysisTool(BaseTool):
    name: str = "Listening Analysis"
    description: str = "Use this tool to analyze IELTS listening responses"

    def _run(self, answers: str) -> str:
        # Заглушка для анализа ответов на аудирование
        return "Listening analysis: 8 out of 10 correct answers."

class SpeakingAnalysisTool(BaseTool):
    name: str = "Speaking Analysis"
    description: str = "Use this tool to analyze IELTS speaking responses"

    def _run(self, transcript: str) -> str:
        # Заглушка для анализа устных ответов
        return "Speaking analysis: Good fluency, needs improvement in pronunciation."

class RecommendationTool(BaseTool):
    name: str = "Recommendation"
    description: str = "Use this tool to get personalized recommendations"

    def _run(self, history: str) -> str:
        prompt = f"Based on the following interaction history, provide a personalized IELTS study recommendation:\n\n{history}"
        recommendation = get_openai_response(prompt)
        return recommendation

class MiniTestTool(BaseTool):
    name: str = "Mini Test"
    description: str = "Use this tool to generate a mini test for practice"

    def _run(self, skill: str) -> str:
        prompt = f"""Generate a short IELTS {skill} mini test with the following format:
        1. A short passage or context (2-3 sentences)
        2. 3 multiple-choice questions related to the passage
        
        Format the output as follows:
        Passage: [Passage or context]
        
        Questions:
        1. [Question 1]
        a) [Option A]
        b) [Option B]
        c) [Option C]
        
        2. [Question 2]
        a) [Option A]
        b) [Option B]
        c) [Option C]
        
        3. [Question 3]
        a) [Option A]
        b) [Option B]
        c) [Option C]
        """
        test = get_openai_response(prompt)
        return test

# Создаем шаблон промпта для агента
template = """You are an IELTS preparation assistant with adaptive learning capabilities. Your goal is to help students improve their IELTS skills.
Given the student's input and conversation history, decide which tool to use for analysis or assistance.

Student input: {input}
Conversation history: {history}

Available tools:
{tools}

Use the following format:

Thought: Consider which tool to use based on the student's input and history
Action: Tool name
Action Input: Relevant part of student input or history for the tool
Observation: Tool output
... (repeat Thought/Action/Observation if needed)
Thought: I have enough information to provide a response to the student
Final Answer: Provide a helpful response to the student based on the tool outputs and conversation history

Begin!

Student input: {input}
{agent_scratchpad}
"""

# Создаем промпт
class CustomPromptTemplate(StringPromptTemplate):
    template: str
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("intermediate_steps")
        history = kwargs.pop("history")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        kwargs["agent_scratchpad"] = thoughts
        kwargs["history"] = history
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        return self.template.format(**kwargs)

# Создаем парсер вывода агента
class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        match = re.search(r"Action: (.*?)[\n]*Action Input:[\s]*(.*)", llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

# Создаем агента
def create_ielts_agent():
    tools = [
        Tool(
            name="Writing Analysis",
            func=WritingAnalysisTool()._run,
            description="Use this tool to analyze IELTS writing tasks"
        ),
        Tool(
            name="Reading Analysis",
            func=ReadingAnalysisTool()._run,
            description="Use this tool to analyze IELTS reading responses"
        ),
        Tool(
            name="Listening Analysis",
            func=ListeningAnalysisTool()._run,
            description="Use this tool to analyze IELTS listening responses"
        ),
        Tool(
            name="Speaking Analysis",
            func=SpeakingAnalysisTool()._run,
            description="Use this tool to analyze IELTS speaking responses"
        ),
        Tool(
            name="Recommendation",
            func=RecommendationTool()._run,
            description="Use this tool to get personalized recommendations"
        ),
        Tool(
            name="Mini Test",
            func=MiniTestTool()._run,
            description="Use this tool to generate a mini test for practice"
        ),
    ]

    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        input_variables=["input", "intermediate_steps", "history"]
    )

    output_parser = CustomOutputParser()

    llm = OpenAI(temperature=0)
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=[tool.name for tool in tools]
    )

    memory = ConversationBufferMemory(memory_key="history")

    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)
    return agent_executor

# Функция для использования агента
def use_ielts_agent(input_text: str, history: List[dict]):
    agent = create_ielts_agent()
    result = agent.run(input=input_text, history=json.dumps(history))
    
    mini_test = None
    listening_text = None
    final_answer = result

    if "Passage:" in result and "Questions:" in result:
        mini_test = extract_mini_test(result)
        final_answer = result.split("Passage:")[0].strip()
    
    if "Listening Text:" in result:
        listening_parts = result.split("Listening Text:")
        listening_text = listening_parts[1].split("Questions:")[0].strip()
        final_answer = listening_parts[0].strip()

    return final_answer, mini_test, listening_text

def extract_mini_test(result):
    passage = result.split("Passage:")[1].split("Questions:")[0].strip()
    questions_part = result.split("Questions:")[1].strip()
    
    questions = []
    for q in questions_part.split("\n\n"):
        q_parts = q.split("\n")
        question = {
            "question": q_parts[0].strip(),
            "options": [opt.strip() for opt in q_parts[1:]]
        }
        questions.append(question)
    
    return {
        "passage": passage,
        "questions": questions
    }
