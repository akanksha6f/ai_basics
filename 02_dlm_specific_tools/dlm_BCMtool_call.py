import json
import httpx
import requests
from requests.auth import HTTPBasicAuth
from pydantic import BaseModel, Field
from gen_ai_hub.proxy.native.openai import chat
from gen_ai_hub.proxy.native.openai import completions
from gen_ai_hub.proxy import get_proxy_client
from gen_ai_hub.proxy.native.openai.clients import OpenAI
from dlm_tool_schema import  get_BCM_request_schema
from dlm_tool_schema import get_all_schemas
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxy_client = get_proxy_client()
chat_client = OpenAI(proxy_client=proxy_client)

import requests

async def aicockpit_get_system_details(
    sid: str = None,
    objid: str = None,
    sysType: str = "ABAPSystem",
    sections: list[str] = None,
    base_url: str = None
) -> str:
    """
    Get comprehensive system details data from AICockpit Provider Final API.
   
    Purpose: Retrieve detailed information for a single system with focused data sections.
    Requirements: Either 'sid' or 'objid' parameter is mandatory for system identification.
   
    Args:
        sid: System ID (optional if objid provided) - preferred identifier
        objid: Object ID (optional if sid provided) - alternative identifier
        sysType: System type (default: ABAPSystem)
        sections: List of section names to retrieve (optional, defaults to ALL)
        base_url: Base URL for the SLIM API (optional, uses environment configuration if not provided)
       
    Returns:
        JSON string with system cockpit data filtered by requested sections.
       
    Available sections with detailed descriptions:
        - system_details: Core system information (SID, status, connections, database, HANA version, app servers, FLP Connections, LPD Connections)
        - Tickets: Monitoring and support data (Sysmon Notes, SNOW tickets, landscape issues, alerts)
        - program_landscape: Program management information (landscape name, responsible persons, milestones, related systems in Landscape)
        - Clients: SAP client configuration (client numbers, descriptions, statuses, roles, customization)
        - Software_Components: Component inventory (versions, service packs, support packages, dependencies)
        - all-sections: All filtered sections combined for comprehensive AI processing
        - ALL: Complete raw cockpit data without any filtering (includes all available data)
       
    Usage examples:
        - Get core system info: sections=["system_details"]
        - Get tickets and issues: sections=["Tickets"]
        - Get complete overview: sections=["all-sections"] or omit sections parameter
    """
    print(f"[aicockpit_get_system_details] called with sid={sid}, objid={objid}, sysType={sysType}, sections={sections}")
   
    try:
        # Validate input parameters
        if not sid and not objid:
            error_msg = "Either 'sid' or 'objid' parameter is required"
            print(f"[aicockpit_get_system_details] {error_msg}")
            return json.dumps({
                "error": error_msg,
                "step": "validation"
            }, indent=2)
       
        # Base URL is now provided by dlm_mcp_server.py
        if base_url is None:
            base_url = "https://dlm/slim/"  # minimal fallback
            print(f"[aicockpit_get_system_details] Using fallback URL: {base_url}")
       
        # Build request payload
        payload = {
            "sysType": sysType
        }
       
        if sid:
            payload["sid"] = sid
        if objid:
            payload["objid"] = objid
        if sections:
            payload["sections"] = sections
       
        url = f"{base_url}/rest/external/aicockpit/systemdata"
        headers = {"Content-Type": "application/json"}
       
        # No authentication needed for SLIM APIs
       
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            print(f"[aicockpit_get_system_details] POST {url} with payload: {json.dumps(payload, indent=2)}")
           
            resp = await client.post(
                url,
                headers=headers,
                json=payload
            )
           
            resp.raise_for_status()
            result = resp.json()
           
            print(f"[aicockpit_get_system_details] Success: status={resp.status_code}")
           
            # Log success with summary
            if isinstance(result, dict):
                if "error" in result:
                    print(f"[aicockpit_get_system_details] API returned error: {result.get('error')}")
                else:
                    # Count sections or data points
                    section_keys = [k for k in result.keys() if k in [
                        "system_details", "Tickets", "Clients", "program_landscape", "Software_Components"
                    ]]
                    if section_keys:
                        print(f"[aicockpit_get_system_details] Successfully retrieved {len(section_keys)} sections: {section_keys}")
                    else:
                        print(f"[aicockpit_get_system_details] Successfully retrieved system data with {len(result)} top-level keys")
           
            return json.dumps(result, indent=2, ensure_ascii=False)
           
    except Exception as exc:
        error_msg = f"Error in aicockpit_get_system_details: {exc}"
        print(f"[aicockpit_get_system_details] {error_msg}")
        return json.dumps({
            "error": error_msg,
            "step": "fetch_system_data"
        }, indent=2)
 
 
async def aicockpit_get_sections(base_url: str = None) -> str:
    """
    Get available sections metadata from AICockpit Provider Final API.
   
    Purpose: Retrieve metadata about all available sections that can be requested
    from aicockpit_get_system_details to understand data structure and capabilities.
   
    Args:
        base_url: Base URL for the SLIM API (optional, uses environment configuration if not provided)
       
    Returns:
        JSON string with sections metadata including:
        - available_sections: List of section objects with name and description
        - total_sections: Total number of available sections
        - description: API description and usage information
       
    Use this tool to:
        - Discover what sections are available for system details retrieval
        - Understand the structure and content of each section
        - Plan which sections to request in aicockpit_get_system_details calls
    """
    print(f"[aicockpit_get_sections] called with base_url={base_url}")
   
    try:
        # Base URL is now provided by dlm_mcp_server.py
        if base_url is None:
            base_url = "https://dlm/slim/"  # minimal fallback
            print(f"[aicockpit_get_sections] Using fallback URL: {base_url}")
       
        url = f"{base_url}/rest/external/aicockpit/sections"
        headers = {"Content-Type": "application/json"}
       
        # No authentication needed for SLIM APIs
       
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            print(f"[aicockpit_get_sections] GET {url}")
           
            resp = await client.get(
                url,
                headers=headers
            )
           
            resp.raise_for_status()
            result = resp.json()
           
            print(f"[aicockpit_get_sections] Success: status={resp.status_code}")
            print(f"[aicockpit_get_sections] Successfully retrieved {result.get('total_sections', 0)} sections")
           
            return json.dumps(result, indent=2, ensure_ascii=False)
           
    except Exception as exc:
        error_msg = f"Error in aicockpit_get_sections: {exc}"
        print(f"[aicockpit_get_sections] {error_msg}")
        return json.dumps({
            "error": error_msg,
            "step": "fetch_sections"
        }, indent=2)

def search_BCM_Request(payload: dict=None,
                       method: str = "POST",
                       endpoint: str = "https://ldciade.wdf.sap.corp:44315/sap/bc/abap/DLMD/BCM_READ_DATA"):
    
    """
    Call BCM API to search the BCM request information based on the dynamic payload created from user prompt.
   example json:
    {
        "HEADER_FILTER": [
            {
                "FIELDNAME": "REQUEST_ID",
                "VALUE_SELOP": [
                    {
                        "SIGN": "I",
                        "OPTION": "EQ",
                        "LOW": "2025000000060"
                    }
                ]
            }
        ],
        "SI_FILTER": [
            {
                "FIELDNAME": "ID",
                "VALUE_SELOP": [
                    {
                        "SIGN": "I",
                        "OPTION": "EQ",
                        "LOW": "ZATT"
                    }
                ]
            }
        ],
        "HEADER_OUT_FEILD":"REQUEST_ID,TA_SID,TA_CLNT",
        "SI_OUT_FEILD":"ID,DESCRIPTION,PROCESSOR"
    }   

    Here in HEADER_OUT_FEILD and SI_OUT_FEILD user can provide the comma separated fields(Technical field name)to be fetched in the output
    """
    user = "DLM_BCM"
    password = "BCM_dlm@321"
    url = f"{endpoint}?sap-client=200&IS_GENERIC=X"  
    print("Calling BCM URL:", url)
    print("Payload:", json.dumps(payload, indent=2))

    headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",   # 👈 critical for SAP services  
    }
   
    resp = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=False,
            auth=HTTPBasicAuth(user, password)   # ✅ CORRECT
        )
    print("🔗 Final URL:", resp.url)
    print("🔒 Response headers:", resp.headers)

 
    print("✅ BCM API call executed.")
    print("🔢 Status Code:", resp.status_code)

    try:
        result = resp.json()
        print("📦 Response (JSON):", json.dumps(result, indent=2))
    except ValueError:
        print("📜 Raw Response:")
        print(resp.text)
    return resp


tools =  []

#tools = [get_BCM_request_schema()] # ✅
tools = get_all_schemas()
print("Tools schema:", tools)

user_prompt = "show me all the BCM request for the system CCF, if it belongs to the landscape: 'SAP S/4HANA Public Cloud Development'?"
system_prompt = """
You are a helpful assistant that retrieves BCM Request information using the BCM POST API CAll.

When the query contains landscape keyword, first call get_aicockpit_get_system_details_schema() tool to get the system ID
and then use BCM API and use system ID as TA_SID from first query and get the BCM request details.

You have to prepare the correct dynamic POST payload based on the user input
You have access to a tool called `search_BCM_Request` that allows you to 
search BCM request based on the filters derived from user prompt.

Reply the output in nauturatl language.
Technical fields are explained below:
- REQUEST_ID: BCM Request ID
- TA_SID: Target System SID
- TA_CLNT: Target System Client
- STATUS: BCM Request Status
- TYPE: BCM Request Type
- CREATED_BY: User who created the BCM Request
- REQUESTOR: User who requested the BCM Request
- ID: Scope Item ID
- DESCRIPTION: Scope Item Description
- PROCESSOR: User responsible for processing the Scope Item
- DELIVERY_STATUS: Status of the Scope Item 

When you need BCM request information, call the tool with the right payload including filters and output fields. Always include the tool result in your final answer.
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user",
    "content": user_prompt
    }
]

print("everything is fine!!")
response = chat_client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)
print(response)
event = response.choices[0].message.tool_calls  # Fully typed Person
print("tool call format is", event)

# completions.model_dump()

def call_function(name, args):
    if name == "get_BCM_Request":
        return search_BCM_Request(**args)
    
tool_calls = getattr(response.choices[0].message, "tool_calls", None)
print("response choices:",response.choices)

if not tool_calls:
    # No tool was called by the model — print assistant content and skip function invocation
    assistant_content = getattr(response.choices[0].message, "content", None)
    print("No tool calls. Assistant response:", assistant_content)
else:   
     # Add the assistant message that initiated the tool call
    messages.append({
        "role": "assistant",
        "content": None,
        "tool_calls": response.choices[0].message.tool_calls
    })

    for tool_call in response.choices[0].message.tool_calls :
        arguments = json.loads(tool_call.function.arguments)

    function_response = call_function(tool_call.function.name, arguments)
    try:
        result_json = function_response.json()
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result_json)
        })
    except Exception:
        messages.append({
        "role": "function",
        "name": tool_call.function.name,
        "content": function_response.text
        }) 

    # print("Message for the second LLM call", messages)
    second_response = chat_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
     )
    
    print(second_response)
    final_response = second_response.choices[0].message.content
    final_message = second_response.choices[0].message
    print("\n================ FINAL RESPONSE ================\n")
    print(final_message.content or "(no content)")
    print("\n===============================================\n")
  