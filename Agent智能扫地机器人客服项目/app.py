import time

import streamlit as st
from agent.react_agent import ReactAgent

# 标题
st.title("智能扫地机器人客服")
st.divider()

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "history_message" not in st.session_state:
    st.session_state["history_message"] = [{"role": "assistant", "content": "你好我是专注回答智能扫地机器人的客服,有什么可以帮到您？"}]

for history_message in st.session_state["history_message"]:
    st.chat_message(history_message["role"]).write(history_message["content"])
# 用户输入提示词
prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["history_message"].append({"role": "user", "content": prompt})

    response_messages = []

    with st.spinner("智能客服思考中。。。。"):
        res_stream = st.session_state["agent"].execute_stream(prompt)


        def capture(generator, cache_list):

            for chunk in generator:
                cache_list.append(chunk)
                # 让流式输出更加顺畅
                for char in chunk:
                    time.sleep(0.01)
                    yield char

        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        st.session_state["history_message"].append({"role": "assistant", "content": response_messages[-1]})
        # 回复完成后刷新页面，这样就只保留回复的内容而没有思考的内容
        st.rerun()
