import nest_asyncio
from typing import Any
import boto3
import json

from llama_index.core.llms import ChatMessage
from llama_index.core.tools import ToolSelection, ToolOutput
from llama_index.core.workflow import Event
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools.types import BaseTool
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, step, Context

from llama_index.program.openai import OpenAIPydanticProgram

from prompts.prompts import SYSTEM_PROMPT_SUBSIDY_REPORT_AGENT

from tools.tool_query_subsidies import query_subsidies, SubsidyReportParameters


class InputEvent(Event):
    input: list[ChatMessage]

class ToolCallEvent(Event):
    tool_calls: list[ToolSelection]


class SubsidyQueryAgent(Workflow):
    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        # initialize the LLM
        model = 'gpt-4o-mini'
        self.llm = OpenAI(model=model, max_tokens=4096)

        # initialize the memory
        self.memory = ChatMemoryBuffer.from_defaults(llm=self.llm)
        self.sources = []

        # initialize the system message
        sys_msg = ChatMessage(role='system', content=SYSTEM_PROMPT_SUBSIDY_REPORT_AGENT)
        self.memory.put(sys_msg)

        # # initialize the tools
        # self.tools = [
        #     FunctionTool.from_defaults(query_subsidies, 
        #                                fn_schema=SubsidyReportParameters
        #                                ),
        # ]


    @step()
    async def agent_director(self, ev: StartEvent | InputEvent) -> ToolCallEvent | StopEvent:
        # clear sources - seems like may be redundant
        self.sources = []

        # get user input
        if isinstance(ev, StartEvent):
            user_input = ev.input
            user_msg = ChatMessage(role='user', content=user_input)
            self.memory.put(user_msg)

        # get chat history
        chat_history = self.memory.get()

        # # call llm with chat history and tools
        # response = await self.llm.achat_with_tools(self.tools, chat_history=chat_history)



        # put that new response into memory
        self.memory.put(response.message)



    #     # call tools -- safely!

    #     tool_calls = self.llm.get_tool_calls_from_response(response, error_on_no_tool_call=False)

    #     if not tool_calls:
    #         return StopEvent(
    #             result={"response": response, "sources": [*self.sources]} # can access this dict from final output
    #         )
    #     else:
    #         return ToolCallEvent(tool_calls=tool_calls)
        
    # @step()
    # async def handle_tool_calls(self, ev: ToolCallEvent) -> InputEvent:
    #     tool_calls = ev.tool_calls
    #     tools_by_name = {tool.metadata.get_name(): tool for tool in self.tools}

    #     tool_msgs = []

    #     # call tools -- safely!
    #     for tool_call in tool_calls:
    #         # fetch the tool which is a BaseTool object
    #         tool = tools_by_name.get(tool_call.tool_name)
    #         additional_kwargs = {
    #             "tool_call_id": tool_call.tool_id, # id associated with ToolSelection object
    #             "name": tool.metadata.get_name(),
    #         }

    #         if not tool: # this is probably the safe part
    #             tool_msgs.append(
    #                 ChatMessage(
    #                     role="tool",
    #                     content = f"Tool {tool_call.tool_name} does not exist",
    #                     additional_kwargs=additional_kwargs # chat message of role tool can also take tool_call_id and name
    #                 )
    #             )
    #             continue

    #         try:
    #             # so you actually execute the tool here with the BaseTool object
    #             # the ToolSelection object has the tool_kwargs that you need to pass to the tool
    #             tool_output = tool(**tool_call.tool_kwargs)

    #             # add the output from the tool to the sources, not sure why at this point
    #             self.sources.append(tool_output)

    #             # append the tool output to the tool messages
    #             tool_msgs.append(ChatMessage(
    #                     role="tool",
    #                     content=tool_output.content,
    #                     additional_kwargs=additional_kwargs
    #                 ))
                
    #             # add all the outputs from the tools into memory as ChatMessages
    #             for msg in tool_msgs:
    #                 self.memory.put(msg)

    #             # get full current chat history
    #             chat_history = self.memory.get()

    #             return InputEvent(input=chat_history)
            
            
    #         except Exception as e:
    #             tool_msgs.append(
    #                 ChatMessage(
    #                     role="tool",
    #                     content=f"Tool {tool.metadata.get_name()} failed to execute: {e}",
    #                     additional_kwargs=additional_kwargs
    #                 )
    #             )

    #             # add all the outputs from the tools into memory as ChatMessages
    #             for msg in tool_msgs:
    #                 self.memory.put(msg)

    #             # get full current chat history
    #             chat_history = self.memory.get()
    #             return InputEvent(input=chat_history)