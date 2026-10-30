from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_chroma import Chroma
from utils.config_handler import chroma_conf, get_abs_path
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=get_abs_path(chroma_conf["persist_directory"])
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def load_document(self):
        """
        从数据文件中读取数据文件，转为向量存入向量库
        需要计算文件的md5值并去重
        """

        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False  # md5没处理过

            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True  # md5处理过

                return False  # md5没处理过

        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path: str):
            if read_path.endswith("txt"):
                return txt_loader(read_path)

            if read_path.endswith("pdf"):
                return pdf_loader(read_path)

            return []

        """
        前面都是定义的工具，工具定义好了接下来就可以使用了，现在要获取文档def load_document(self):
        把文档都用这些工具处理成md5值存到md5文件中，所以现在要使用listdir_with_allowed_type这个方法去获取能被允许
        获得的文件类型，这样才能读到我们想要读取的类型，不至于读取其他文件（如上定义只想读文件夹下的txt和pdf）
        
        所以调用vs.load_document()时这里才是程序的入口，从这里先获取允许的类型，经过listdir_with_allowed_type
        返回元组，元组里面的每一个元素对应一个路径，路径下有对应的文件，然后for循环进行获取文件的md5，该文件的md5不存在就加载到向量库中
        """
        allowed_files_path: list[str] = listdir_with_allowed_type(
            # 这里是获取路径data，路径下是文件，判断哪些文件的后缀格式是允许读的，然后借助listdir_with_allowed_type整理成列表返回
            get_abs_path(chroma_conf["data_path"]),                # 这里是获取data路径
            tuple(chroma_conf["allow_knowledge_file_type"])         # 获取被允许读的文件后缀
        )

        for path in allowed_files_path:
            # 获取文件的md5
            md5_hex = get_file_md5_hex(path)

            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在知识库中，跳过")
                continue        # 立即跳到下一个 path，后面代码全不执行,直接跳到for循环的下一轮，下一个path进行检查

            try:
                documents: list[Document] = get_file_documents(path)    # 获取文件内容

                if not documents:       # 如果文件中没有内容
                    logger.warning(f"[加载知识库]{path}没有有效文本内容，跳过")
                    continue

                split_document: list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片没有有效文本内容，跳过")
                    continue

                # 经过上面一系列判断后，最终有效的不在知识库中的文本内容就会从这存到向量库中
                self.vector_store.add_documents(split_document)

                # 记录这个已经处理好的文件的md5，避免下次重复加载
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]{path}内容加载成功")
            except Exception as e:
                # exc_info为True会记录详细的报错堆栈，如果为False仅记录错误信息本身
                logger.error(f"[加载知识库]{path}失败：{str(e)}", exc_info=True)        # str(e)是把错误转成字符串打印
                continue


if __name__ == '__main__':
    # 创建实例对象
    vs = VectorStoreService()
    # 加载知识库，
    vs.load_document()
    # 加载完知识库后拿到检索器
    retriever = vs.get_retriever()
    # 通过检索器注入米兰关键字
    res = retriever.invoke("迷路")
    for r in res:
        print(r.page_content)
        print("="*20)
