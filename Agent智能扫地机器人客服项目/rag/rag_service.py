"""
后续的智能体构建并不是只根据RAG检索的资料回复，RAG只是一个小环节。其作用是：
总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复。这里并不是最终回复，RAG只是
         一个工具
"""
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from model.factory import chat_model
from langchain_core.documents import Document


def print_prompt(prompt):
    print("="*30)
    print(prompt.to_string())
    print("="*30)
    return prompt


class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()             # 步骤1：调用函数 → 拿到字符串(文本内容)
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)     # 步骤2：把字符串 → 模板对象
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain

    # query是用户提问，用户输入的信息要查询什么东西
    def retriever_docs(self, query: str) -> list[Document]:
        # 把用户提问输入进去就能检索到相关的参考资料
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        # 检索器返回的是list[Document]对象，上面函数也有体现
        context_docs = self.retriever_docs(query)

        # 把参考资料拼接成字符串
        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】：参考资料内容：{doc.page_content} | 参考元数据：{doc.metadata}\n"

        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )


if __name__ == '__main__':
    rag = RagSummarizeService()

    print(rag.rag_summarize("小户型适合什么扫地机器人？"))
