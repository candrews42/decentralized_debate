import logging
from typing import Dict, Any
import aiohttp
from .plugin import Plugin

class NewEntryPlugin(Plugin):
    """
    A plugin to log Telegram bot messages to the debate.
    """

    def get_source_name(self) -> str:
        return "newEntry"

    def get_spec(self) -> [Dict]:
        return [
            {
                "name": "newEntry",
                "description": "Log a Telegram bot message to the debate.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entry": {"type": "string", "description": "The text of the debate entry."}
                    },
                    "required": ["entry"]
                }
            }
        ]

    async def execute(self, function_name: str, helper, **kwargs) -> Dict[str, Any]:
        logging.info(f"Executing function: {function_name} with arguments: {kwargs}")

        if function_name != "newEntry":
            error_message = f"Unknown function: {function_name}"
            logging.error(error_message)
            raise ValueError(error_message)

        url = "https://p3mxly.buildship.run/debateStatus"
        headers = {
            "Content-Type": "application/json"
        }

        # Map 'entry' input to 'message' for the API request
        body = {
            "message": kwargs["entry"]
        }

        logging.debug(f"Prepared request body: {body}")
        logging.debug(f"Sending POST request to {url} with headers {headers}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=body, headers=headers) as response:
                status = response.status
                response_text = await response.text()
                logging.debug(f"Received response: {status} - {response_text}")

                # Attempt to parse the response as JSON
                try:
                    response_data = await response.json()
                    logging.info(f"Request successful, received JSON data: {response_data}")
                except aiohttp.ContentTypeError:
                    response_data = {"response": response_text}
                    logging.warning(f"Response is not JSON: {response_text}")

                # Handle the response
                if status in range(200, 300):
                    return {
                        "status": status,
                        "data": response_data
                    }
                else:
                    error_message = f"Request failed: {status} - {response_data}"
                    logging.error(error_message)
                    return {
                        "status": status,
                        "error": response_data
                    }
