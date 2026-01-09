import requests
from typing import Any, Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import AVASecret

class NIHRePORTERAPIConnectorSchema(BaseModel):
    """
    Input schema for NIHRePORTERAPIConnector.
    """
    query: str = Field(..., description="Search query string to filter NIH grants and projects. Can include keywords, PI names, institutions, etc.")
    fiscal_year: Optional[int] = Field(None, description="Fiscal year to filter the grants/projects. Optional.")
    project_activity: Optional[str] = Field(None, description="Project activity code (e.g., R01, K99) to filter results. Optional.")
    org_name: Optional[str] = Field(None, description="Name of the organization/institution to filter results. Optional.")
    pi_name: Optional[str] = Field(None, description="Name of the Principal Investigator to filter results. Optional.")
    limit: Optional[int] = Field(10, description="Maximum number of results to return. Default is 10.")

class NIHRePORTERAPIConnector(BaseTool):
    """
    NIHRePORTERAPIConnector - A tool to query the NIH RePORTER MCP Server for grant and project information.
    """
    name: str = "NIH RePORTER API Connector"
    description: str = "A tool to query the NIH RePORTER MCP Server for grant and project information."
    args_schema: Type[BaseModel] = NIHRePORTERAPIConnectorSchema
    base_url: str = 'https://api.reporter.nih.gov/v2/projects/search'

    def _run(self, query: str, fiscal_year: Optional[int] = None, project_activity: Optional[str] = None, org_name: Optional[str] = None, pi_name: Optional[str] = None, limit: Optional[int] = 10) -> str:
        try:
            api_key = AVASecret.getValue("NIH_REPORTER_API_KEY")
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key
            }

            criteria = {
                "criteria": {
                    "text": query
                },
                "include_fields": [
                    "project_title", "project_num", "contact_pi_name", "organization_name", "award_amount", "fiscal_year", "project_start_date", "project_end_date", "abstract_text"
                ],
                "offset": 0,
                "limit": limit
            }

            if fiscal_year:
                criteria["criteria"]["fiscal_years"] = [fiscal_year]
            if project_activity:
                criteria["criteria"]["activity_codes"] = [project_activity]
            if org_name:
                criteria["criteria"]["org_names"] = [org_name]
            if pi_name:
                criteria["criteria"]["pi_names"] = [pi_name]

            response = requests.post(self.base_url, json=criteria, headers=headers)
            response.raise_for_status()
            return f"NIH RePORTER API Results: {response.json()}"
        except requests.RequestException as e:
            return f"Error querying NIH RePORTER API: {str(e)}"