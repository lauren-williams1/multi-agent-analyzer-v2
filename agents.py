# agents.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from sample_data import get_relevant_data
import json
import os

# Initialize LLM
def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")
    
    # Simplified initialization - no extra kwargs
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=api_key  # Changed from api_key to openai_api_key
    )


class DataCollectorAgent:
    """Gathers relevant business data based on query"""
    
    def __init__(self):
        self.name = "Data Collector"
        self.llm = get_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a data collection specialist. 
            You have been provided with actual business data below.
            
            Analyze the data and present the most relevant metrics for the user's query.
            Format your response clearly with the key data points.
            
            Available Data:
            {data}
            
            Extract and present the most relevant information for the query.
            """),
            ("user", "{query}")
        ])
    
    def execute(self, query: str) -> dict:
        """Execute data collection agent"""
        # Get relevant sample data based on query
        data_package = get_relevant_data(query)
        
        # Format data as JSON string
        data_json = json.dumps(data_package["data"], indent=2)
        
        chain = self.prompt | self.llm
        response = chain.invoke({
            "query": query,
            "data": data_json
        })
        
        result = {
            "agent": self.name,
            "output": response.content,
            "status": "completed",
            "data_source": data_package["data_source"]
        }
        
        return result


class AnalysisAgent:
    """Analyzes data and identifies trends/patterns"""
    
    def __init__(self):
        self.name = "Analysis Agent"
        self.llm = get_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a business data analyst.
            Given collected data points, perform analysis and identify:
            1. Key trends
            2. Patterns
            3. Anomalies
            4. Correlations
            
            Be specific and quantitative where possible.
            """),
            ("user", """Business Query: {query}
            
            Data Collected: {data_collected}
            
            Perform detailed analysis:""")
        ])
    
    def execute(self, query: str, data_collected: str) -> dict:
        """Execute analysis agent"""
        chain = self.prompt | self.llm
        response = chain.invoke({
            "query": query,
            "data_collected": data_collected
        })
        
        result = {
            "agent": self.name,
            "output": response.content,
            "status": "completed"
        }
        
        return result


class InsightsAgent:
    """Generates actionable recommendations"""
    
    def __init__(self):
        self.name = "Insights Agent"
        self.llm = get_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a business strategy consultant.
            Given data analysis, provide:
            1. Top 3 actionable insights
            2. Specific recommendations
            3. Potential risks to consider
            4. Next steps
            
            Be concrete and business-focused.
            """),
            ("user", """Business Query: {query}
            
            Analysis Results: {analysis}
            
            Generate strategic insights:""")
        ])
    
    def execute(self, query: str, analysis: str) -> dict:
        """Execute insights agent"""
        chain = self.prompt | self.llm
        response = chain.invoke({
            "query": query,
            "analysis": analysis
        })
        
        result = {
            "agent": self.name,
            "output": response.content,
            "status": "completed"
        }
        
        return result