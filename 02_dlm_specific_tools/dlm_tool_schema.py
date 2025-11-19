def get_weather_schema():

    return [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a given latitude and longitude.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "The latitude of the location to get the weather for.",
                        },
                        "longitude": {
                            "type": "number",
                            "description": "The longitude of the location to get the weather for.",
                        },
                    },
                    "required": ["latitude", "longitude"],
                    "additionalProperties": False,
                },
                "strict": True,
            },

        }
    ]

# tool_schemas/tool_schemas.py

def get_search_system_flexi_schema():
    """Schema for /report/flexi (field-based search)."""
    return {
        "type": "function",
        "function": {
            "name": "search_system_flexi",
            "description": (
                "Query the SLIM Flexi Report API to search SAP system landscape data. "
                "Use a comma-separated field list (supports dot notation and aliases)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "enum":["systemType", "extSystem","sid","landscape"],
                         "description": (
                            "Comma-separated list of fields to retrieve, with optional filters. "
                            "Filters are encoded as 'field|value'. "
                            "Example: 'SID,systemType,status,customer.name,sid|ER1,status|Live'. "
                            " Rules: 'sid|...' is only valid for a specific 3-character SID. "
                            "To query multiple systems, use only other filters like 'status|Parked'."
                            "for an extensibility system, please make sure that the flag extSystem is true."),                            
                            },
                        "otype": {
                        "type": "string",
                        "enum": ["json", "xml", "csv"],
                        "default": "json",
                        "description": "Output format (default: json)."
                    }
                },
                "required": ["query", "otype"],
                "additionalProperties": False
            },
            "strict": True
        }
    }


def get_entity_details_schema():
    """
    Schema for /rest/entityData/get/{entity} supporting:
      - Systems (model.system.ABAPSystem)
      - Landscapes (model.Landscape)
    Filters map to repeated qFieldValue params: field~value
    Examples:
      - status=parked: qFieldValue=status~parked
      - SID=ADL: qFieldValue=SID~ADL
      - Landscape name=CRM 714: qFieldValue=name~CRM%20714
      - AND across multiple qFieldValue; OR may require backend-specific encoding.
    """
    return {
        "type": "function",
        "function": {
            "name": "get_entity_details",
            "description": (
                "Fetch entity data from /rest/entityData/get/{entity}. "
                "Supports systems (model.system.ABAPSystem) and landscapes (model.Landscape). "
                "Returns one or many entries depending on filters."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "enum": ["model.system.ABAPSystem", "model.Landscape"],
                        "description": "Target entity to query."
                    },
                    "filters": {
                        "type": "array",
                        "description": (
                            "List of filters mapped to qFieldValue as 'field~value'. "
                            "Multiple entries are ANDed by default."
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {
                                    "type": "string",
                                    "description": "Entity attribute to match (e.g., 'SID', 'status', 'name', 'product.name', 'usage')."
                                },
                                "value": {
                                    "type": "string",
                                    "description": "Match value; '~' semantics as per backend (typically contains/equals). URL-encode if needed."
                                }
                            },
                            "required": ["field", "value"],
                            "additionalProperties": False
                        }
                    },
                    "logic": {
                        "type": "string",
                        "enum": ["AND", "OR"],
                        "description": (
                            "How to combine filters. Backend natively ANDs repeated qFieldValue. "
                            "OR may require encoding multiple values per field or backend support."
                        )
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Optional client-side limit on returned items."
                    },
                    "offset": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "Optional client-side offset (if you implement pagination)."
                    },
                    "q_raw": {
                        "type": "array",
                        "description": (
                            "Advanced: pass-through list of raw qFieldValue strings ('field~value'). "
                            "If provided, these are appended as-is."
                        ),
                        "items": {"type": "string"}
                    }
                },
                "required": ["entity"],
                "additionalProperties": False
            },
            "strict": True
        }
    }


def get_all_schemas():
    """Convenience: return both tool schemas as a list."""
    return [get_search_system_flexi_schema(), get_entity_details_schema()]

def get_BCM_request_schema( ):
    """ BCM (Business Client Management) is a DLM-specific tool used for client setup inside SAP systems.
    User Groups:
        - Requestor: Creates BCM requests for new clients
        - Technical Expert / COE / Expert
        - Request Manager
        - Guest

    A BCM request consists of multiple sections such as Header, Details, and Scope Items.

    This schema defines a generic API call to fetch BCM request details.
    The input parameters are dynamic based on user requirements.
    """
    return {
        "type": "function",
        "function": {
            "name": "get_BCM_Request",
            "description": (
                "Execute a POST call to the BCM (Business Client Management) service "
                "to fetch client request details. it's a POST call and the payload are craeted dynamically based on the user input"
           ),
            "parameters": {
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "The API endpoint to call BCM service.",
                        "default": "https://ldciade.wdf.sap.corp:44315/sap/bc/abap/DLMD/BCM_READ_DATA?sap-client=200&IS_GENERIC=X"  
                    },
                    "method": {
                        "type": "string",
                        "enum": ["POST"],
                        "default": "POST",
                        "description": "The HTTP method to be used for the call."
                    },
                    "payload": {
                        "type": "object",
                        "description": "POST body payload for the BCM API call.",
                        "properties": {
                            "HEADER_FILTER": {
                                "type": "array",
                                "description": """This array will be formed based on user input
                                                this filiter criteria will be used for fetching data from ABAP SE11 table /DLMD/2BCPR_MSTR """,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "FIELD_NAME": {
                                            "type": "string",
                                            "description": """Technical name of the field, determined based on user prompt,"
                                                            e.g., 'REQUEST_ID', 'VERSION', 'STATUS', 'REQUESTOR', 'TYPE', etc.
                                                            All the field name should be part of /DLMD/2BCPR_MSTR table fields""",
                                           "enum":[] },
                                        "VALUE_SELOP": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "SIGN": {
                                                        "type": "string",
                                                        "description": "I = Include if the value should be included or E = Exclude if the value should be excluded.",
                                                        "valid enum": ["I", "E"]
                                                    },
                                                    "OPTION": {
                                                        "type": "string",
                                                        "description": """The operators determine whether the specified values are used as a single value, a range or a search pattern when restricting the data selection. 
                                                        These operators work together with the fields lower limit (LOW), upper limit (HIGH) and the OPTION (I/E).
                                                        The following operators may be used:
                                                        EQ Equal
                                                        BT BeTween
                                                        LE Less Equal
                                                        GE Greater Equal
                                                        CP Contains Pattern""",
                                                        "valid enum": ["EQ", "GE", "LE", "BT", "NB", "CP"]
                                                    },
                                                    "LOW": {
                                                        "type": "string",
                                                        "description": "The lower limit of the value range for the filter condition."
                                                    },
                                                    "HIGH": {"type": "string",
                                                    "description": "The upper limit of the value range for the filter condition."
                                                    }
                                                },
                                                "required": ["SIGN", "OPTION", "LOW"]
                                            }
                                        }
                                    },
                                    "required": ["FIELD_NAME", "VALUE_SELOP"]
                                }
                            }
                            },
                            "HEADER_OUT_FEILD": {
                                "type": "string",
                                "description": """Comma-separated list of fields to retrieve in the response.
                                                e.g., 'REQUEST_ID,VERSION,STATUS,REQUESTOR,TYPE'""",
                            }
                        },
                        "required": ["HEADER_FILTER, HEADER_OUT_FEILD"]
                    }
                }
            }
        }
  