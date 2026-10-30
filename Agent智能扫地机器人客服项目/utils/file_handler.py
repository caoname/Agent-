import os
import hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


# 想要计算文件的md5必须使用二进制，也就是rb
def get_file_md5_hex(filepath: str):             # 获取文件的md5十六进制字符串
    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]路径{filepath}不是文件")
        return

    md5_obj = hashlib.md5()

    chunk_size = 4096     # 4KB分片，避免文件过大爆内存
    try:
        with open(filepath, "rb") as f:         # 必须是二进制
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
            """
            等价于下面的写法：
            chunk = f.read(chunk_size)
            while chunk:
                md5_obj.update(chunk_size)
                chunk = f.read(chunk_size)
            """
            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败。{str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):            # 返回文件夹内的文件列表（可自定义想要获取文件后缀）
    """
    给定一个路径，路径下是文件夹，判断哪些文件的后缀格式是允许读的，然后整理成列表返回
    """
    files = []

    if not os.path.isdir(path):
        logger.error(f"传入的文件类型[listdir_with_allowed_type]不是文件夹")
        return allowed_types

    # 如果是文件夹的话，就列出文件夹中的内容
    for f in os.listdir(path):
        if f.endswith(allowed_types):           # 如果传入的文件类型是允许的，进入下一步
            files.append(os.path.join(path, f))     # 把路径和文件名拼接才是完整路径,进行返回

    return tuple(files)


def pdf_loader(filepath: str, password=None) -> list[Document]:
    return PyPDFLoader(filepath, password).load()       # 全量加载


# 必须是utf8，要不然默认gbk会报错
def txt_loader(filepath: str) -> list[Document]:
    return TextLoader(filepath, encoding="utf-8").load()



