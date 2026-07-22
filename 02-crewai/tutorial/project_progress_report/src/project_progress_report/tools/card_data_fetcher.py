from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import os

# 1. UNCOMMENTED AND RENAMED: This forces the AI to provide exactly what we need.
class CardDataFetcherInput(BaseModel):
    """Input schema for CardDataFetcherTool."""
    card_id: str = Field(..., description="The exact Trello ID of the card you want to fetch.")

class CardDataFetcherTool(BaseTool):
    name: str = "Trello Card Data Fetcher"
    description: str = "Fetches detailed data for a single specific card from a Trello board."
    
    # Link the schema to the tool
    args_schema: Type[BaseModel] = CardDataFetcherInput

    # 2. RESTORED: We need the credentials here so self.api_key works!
    api_key: str = os.getenv('TRELLO_API_KEY', '') 
    api_token: str = os.getenv('TRELLO_API_TOKEN', '') 

    # 3. FIXED: The parameter is now exactly 'card_id', matching the Pydantic schema
    def _run(self, card_id: str) -> dict:
        url = f"{os.getenv('DLAI_TRELLO_BASE_URL', 'https://api.trello.com')}/1/cards/{card_id}"
        
        query = {
            'key': self.api_key,
            'token': self.api_token
        }
        
        response = requests.get(url, params=query)

        if response.status_code == 200:
            return response.json()
        else:
            # 4. FIXED: Removed json.dumps() to return a proper dictionary
            return {"error": f"Failed to fetch card data for {card_id}, do not try to fetch any Trello data anymore."}