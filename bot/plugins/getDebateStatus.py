import logging
import os
from typing import Dict, Any
from supabase import create_client, Client
from .plugin import Plugin

class DebateStatusPlugin(Plugin):
    """
    A plugin to retrieve the current status and question of the debate from the Supabase database.
    """
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    def get_source_name(self) -> str:
        return "debateStatus"

    def get_spec(self) -> [Dict]:
        return [
            {
                "name": "getDebateStatus",
                "description": "Retrieve the current status and question of the debate from the Supabase database.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    async def execute(self, function_name: str, helper, **kwargs) -> Dict[str, Any]:
        logging.info(f"Executing function: {function_name}")
        if function_name != "getDebateStatus":
            error_message = f"Unknown function: {function_name}"
            logging.error(error_message)
            raise ValueError(error_message)

        try:
            # Query the state_of_debate and debate_question columns from the state_of_debate table
            response = self.supabase.table("state_of_debate").select("state_of_debate,debate_question").order('id', desc=True).limit(1).execute()

            # Check if we got any data
            if response.data:
                debate_status = response.data[0]['state_of_debate']
                debate_question = response.data[0]['debate_question']
                logging.info(f"Retrieved debate status: {debate_status}")
                logging.info(f"Retrieved debate question: {debate_question}")
                return {
                    "status": 200,
                    "data": {
                        "state_of_debate": debate_status,
                        "debate_question": debate_question
                    }
                }
            else:
                logging.warning("No debate status or question found in the database")
                return {
                    "status": 404,
                    "error": "No debate status or question found"
                }
        except Exception as e:
            error_message = f"Failed to retrieve debate status and question: {str(e)}"
            logging.error(error_message)
            return {
                "status": 500,
                "error": error_message
            }