"""
主要作用就是如果用户有生成报告的意图，就进行拦截动作，把提示词换成新的重新运行模型
"""
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from typing import Callable
from utils.logger_handler import logger
from utils.prompt_loader import load_system_prompts, load_report_prompts
"""
两个入参的理解，langchain去调用工具本质上还是调用一个函数，而调用函数除了调用函数本身
还需要函数的传入参数。写这两个参数的目的是拿到传入monitor_tool中的参数，以及该方法本身并且在方法
内部进行使用吗？不仅可以使用还可以在使用前自己自定义一些其他的功能等
"""


# 用装饰器来实现监管功能，其入参有两个
@wrap_tool_call
def monitor_tool(

        # 请求的数据封装，可以理解为传入参数,(想执行的工具名字被记录到 request 里)
        request: ToolCallRequest,
        # 执行的函数本身，只有执行 handler(request) 时，工具才真正运行,
        # handler 拿到 request 后，就会去运行 request 里记录的那个工具函数
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    logger.info(f"[monitor_tool]执行工具：{request.tool_call['name']}")
    logger.info(f"[monitor_tool]传入参数：{request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"[monitor_tool]工具{request.tool_call['name']}调用成功")

        # 如果调用这个fill_context_for_report函数就表明需要写报告，但是只是把标志改成True，
        # 具体什么时候转换提示词在下面report_prompt_switch方法中
        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True
        return result
    except Exception as e:
        logger.error(f"工具：{request.tool_call['name']}调用失败，原因：{str(e)}")
        raise e


@before_model
def log_before_model(
        # 可以通过下面拿到当前模型/agent执行前的状态和信息
        state: AgentState,          # 整个Agent智能体中的状态记录
        runtime: Runtime,           # 记录了整个执行过程中的上下文信息
):
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息")

    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")
    return None


# 用户在提问时如果有生成报告的意图，就需要把原本的提示词动态的
# 转为生成报告的提示词，也就是完成提示词切换，更好的生成报告
@dynamic_prompt                 # 每次生成提示词之前，调用此函数，以此判断需要在这个函数中使用哪个提示词
def report_prompt_switch(request: ModelRequest):     # 动态切换提示词
    # 通过这一系列去获取monitor_tool函数中的report的值，如果没有值默认为False。为True则继续下一步
    is_report = request.runtime.context.get("report", False)
    if is_report:
        print("="*20 + "我真的使用报告提示词了哦" + "="*20)
        return load_report_prompts()

    return load_system_prompts()






