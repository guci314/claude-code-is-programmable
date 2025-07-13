#!/usr/bin/env python3
"""
MCP Calculator Server
A simple calculator server implementing the Model Context Protocol
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict, List, Optional
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPCalculatorServer:
    """MCP Calculator Server implementation"""
    
    def __init__(self):
        self.name = "calculator"
        self.version = "1.0.0"
        
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }
    
    async def handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": [
                {
                    "name": "calculate",
                    "description": "Perform mathematical calculations. Supports basic arithmetic (+, -, *, /, //, %, **), trigonometry (sin, cos, tan), and other math functions (sqrt, log, exp, abs).",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4', 'sqrt(16)', 'sin(pi/2)')"
                            }
                        },
                        "required": ["expression"]
                    }
                },
                {
                    "name": "convert_units",
                    "description": "Convert between different units (length, weight, temperature)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "number",
                                "description": "The value to convert"
                            },
                            "from_unit": {
                                "type": "string",
                                "description": "The unit to convert from (e.g., 'meters', 'feet', 'celsius', 'fahrenheit', 'kg', 'pounds')"
                            },
                            "to_unit": {
                                "type": "string",
                                "description": "The unit to convert to"
                            }
                        },
                        "required": ["value", "from_unit", "to_unit"]
                    }
                }
            ]
        }
    
    async def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "calculate":
            return await self._calculate(arguments)
        elif tool_name == "convert_units":
            return await self._convert_units(arguments)
        else:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    async def _calculate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform mathematical calculation"""
        expression = args.get("expression", "")
        
        try:
            # Create a safe environment for eval
            safe_dict = {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                'pow': pow,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'pi': math.pi,
                'e': math.e
            }
            
            # Remove potentially dangerous operations
            dangerous_patterns = ['__', 'import', 'exec', 'eval', 'open', 'file', 'input', 'compile']
            for pattern in dangerous_patterns:
                if pattern in expression.lower():
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error: Expression contains potentially dangerous operation: {pattern}"
                            }
                        ]
                    }
            
            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"{expression} = {result}"
                    }
                ]
            }
            
        except ZeroDivisionError:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: Division by zero"
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ]
            }
    
    async def _convert_units(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Convert between units"""
        value = args.get("value", 0)
        from_unit = args.get("from_unit", "").lower()
        to_unit = args.get("to_unit", "").lower()
        
        # Unit conversion factors
        conversions = {
            # Length
            ("meters", "feet"): 3.28084,
            ("feet", "meters"): 0.3048,
            ("meters", "inches"): 39.3701,
            ("inches", "meters"): 0.0254,
            ("kilometers", "miles"): 0.621371,
            ("miles", "kilometers"): 1.60934,
            
            # Weight
            ("kg", "pounds"): 2.20462,
            ("pounds", "kg"): 0.453592,
            ("grams", "ounces"): 0.035274,
            ("ounces", "grams"): 28.3495,
            
            # Temperature (special handling)
            ("celsius", "fahrenheit"): lambda c: c * 9/5 + 32,
            ("fahrenheit", "celsius"): lambda f: (f - 32) * 5/9,
            ("celsius", "kelvin"): lambda c: c + 273.15,
            ("kelvin", "celsius"): lambda k: k - 273.15,
        }
        
        try:
            key = (from_unit, to_unit)
            if key in conversions:
                conversion = conversions[key]
                if callable(conversion):
                    result = conversion(value)
                else:
                    result = value * conversion
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"{value} {from_unit} = {result:.4f} {to_unit}"
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: Cannot convert from {from_unit} to {to_unit}"
                        }
                    ]
                }
                
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ]
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_list_tools(params)
            elif method == "tools/call":
                result = await self.handle_call_tool(params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """Run the MCP server"""
        logger.info(f"Starting MCP Calculator Server v{self.version}")
        
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        writer = sys.stdout
        
        while True:
            try:
                # Read input line by line
                line = await reader.readline()
                if not line:
                    break
                
                # Parse JSON-RPC request
                request = json.loads(line.decode('utf-8'))
                logger.info(f"Received request: {request.get('method')}")
                
                # Handle request
                response = await self.handle_request(request)
                
                # Send response
                response_str = json.dumps(response) + '\n'
                writer.write(response_str.encode('utf-8'))
                writer.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"Server error: {e}")

async def main():
    """Main entry point"""
    server = MCPCalculatorServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())