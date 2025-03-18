from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from typing import List
import asyncio
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from core.exceptions import ModelProcessingError, APIKeyError, CompetitiveResearchException
from schemas.models import ResearchReport


class CompetitiveResearchAgent:
    def __init__(self, groq_api_key: str):
        try:
            # Initialize ChatGroq model with the provided API key.
            self.llm = ChatGroq(
                model="mixtral-8x7b-32768",
                api_key=groq_api_key
            )
            # Load the SerpAPI tool directly via load_tools.
            self.tools = load_tools(["serpapi"], llm=self.llm)
            self.agent = self._create_agent()
        except Exception as e:
            raise APIKeyError(f"Error initializing agent: {str(e)}")

    def _create_agent(self) -> AgentExecutor:
        try:
            # Prepare static values for the prompt.
            tools_list = "\n".join(
                [f"- {tool.name}: {tool.description}" for tool in self.tools])
            tool_names = ", ".join([tool.name for tool in self.tools])

            # Load the agent prompt template from an external .jinja file.
            env = Environment(loader=FileSystemLoader("templates"))
            template = env.get_template("agent_prompt.jinja")
            # Render only the static parts (tools and tool_names)
            rendered_template = template.render(
                tools=tools_list,
                tool_names=tool_names
            )
            # Create a PromptTemplate that still requires "input" and "agent_scratchpad" at runtime.
            prompt = PromptTemplate(
                template=rendered_template,
                input_variables=["query"]
            )

            print(prompt.format)
            agent = create_structured_chat_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            return AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=5,
                early_stopping_method="generate"
            )
        except Exception as e:
            raise ModelProcessingError(f"Error creating agent: {str(e)}")

    async def generate_report(self, competitors: List[str],
                              start_date: datetime,
                              end_date: datetime) -> ResearchReport:
        """
        Generates a competitive research report by instructing the agent to perform all
        competitive research tasks in one comprehensive query.
        """
        try:
            # Build the comprehensive query.
            query = (
                f"Perform a competitive research analysis for the following competitors: {', '.join(competitors)}. "
                f"Analyze their latest news on pricing, product launches, funding, partnerships, and market positioning "
                f"for the period from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}. "
                "Provide a detailed markdown report that includes separate sections for each competitor, a strategic summary, "
                "and actionable recommendations."
            )
            # Invoke the agent. Its internal chain (using its prompt template) handles the search and analysis.
            final_report = await self.agent.arun(query)

            return ResearchReport(
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                summary=final_report,
                generated_at=datetime.now()
            )
        except Exception as e:
            raise CompetitiveResearchException(
                f"Unexpected error in report generation: {str(e)}")
