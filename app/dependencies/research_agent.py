from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from typing import List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from core.exceptions import ModelProcessingError, APIKeyError, CompetitiveResearchException
from schemas.models import ResearchReport
from core.config import settings


class CompetitiveResearchAgent:
    def __init__(self, groq_api_key: str):
        try:
            # Initialize ChatGroq model with the provided API key.
            self.llm = ChatGroq(
                model="gemma2-9b-it",
                api_key=groq_api_key
            )
            # Load the SerpAPI tool directly via load_tools.
            self.tools = load_tools(
                ["serpapi"], llm=self.llm, serpapi_api_key=settings.SERPAPI_API_KEY
            )
            self.agent = self._create_agent()
        except Exception as e:
            raise APIKeyError(f"Error initializing agent: {str(e)}")

    def _create_agent(self) -> AgentExecutor:
        try:
            # Prepare static parts: list of tools and tool names.
            tools_list = "\n".join(
                [f"- {tool.name}: {tool.description}" for tool in self.tools])
            tool_names = ", ".join([tool.name for tool in self.tools])

            # Load the agent prompt template from an external .jinja file.
            env = Environment(loader=FileSystemLoader("templates"))

            # Instead of rendering the template here, we use its raw source and pass partial variables.
            raw_template, _, _ = env.loader.get_source(
                env, "agent_prompt.jinja")

        # Create a PromptTemplate that requires "input" and "agent_scratchpad" as dynamic variables.
            prompt = PromptTemplate(
                template=raw_template,
                input_variables=["input", "agent_scratchpad",
                                 "tools", "tool_names"],
                partial_variables={
                    "tools": tools_list,
                    "tool_names": tool_names,
                    "agent_scratchpad": ""  # default value for scratchpad
                }
            )
            agent = initialize_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )

            return agent
        except Exception as e:
            raise ModelProcessingError(f"Error creating agent: {str(e)}")

    async def generate_report(self, competitors: List[str],
                              start_date: datetime,
                              end_date: datetime) -> ResearchReport:
        """
        Generates a competitive research report by instructing the agent to perform all competitive research tasks
        for the given competitors and time period, then returns a complete markdown report.
        """
        try:
            query = (
                f"Perform a competitive research analysis for the following competitors: {competitors}). "
                f"Analyze their latest news on pricing, product launches, funding, partnerships, and market positioning "
                f"for the period from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}. "
                "Provide a detailed markdown report with separate sections for each competitor, a strategic summary, "
                "and actionable recommendations."
            )
            # Call the agent with the required variables: input and agent_scratchpad.
            final_report = await self.agent.ainvoke({'input': query})

            # Debug print to inspect the agent output.
            print("DEBUG: Raw agent output:", final_report)

            return ResearchReport(
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                summary=final_report['output'],
                generated_at=datetime.now()
            )
        except Exception as e:
            raise CompetitiveResearchException(
                f"Unexpected error in report generation: {str(e)}")
