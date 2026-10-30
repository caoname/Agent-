from langchain.chat_models import init_chat_model, BaseChatModel
from abc import ABC, abstractmethod
from typing import Optional
from langchain_ollama import OllamaEmbeddings
from langchain_core.embeddings import Embeddings
from utils.config_handler import rag_conf
from dotenv import load_dotenv
import os
load_dotenv()


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    # 子类继承父类，若父类内容为空，子类必须对父类中定义的方法进行重写
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return init_chat_model(
            model=rag_conf["chat_model_name"],
            model_provider="openai",
            api_key=os.getenv(rag_conf["api_key"]),
            base_url=rag_conf["base_url"]
        )


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return OllamaEmbeddings(model=rag_conf["embedding_model_name"])


# 分别创建对应聊天模型的实例对象
chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
