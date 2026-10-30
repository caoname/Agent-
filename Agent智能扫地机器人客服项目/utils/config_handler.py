"""
yaml 格式是工程项目中常用的配置文件格式，类似字典的k：v形式，就可以管理配置项
k:v
"""
import yaml
from utils.path_tool import get_abs_path


# 加载和rag相关的配置文件
def load_rag_config(config_path: str = get_abs_path("config/rag.yaml"), encoding: str = "utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)             # 全量加载？yaml通过k获得v？


# 加载和chroma相关的配置文件
def load_chroma_config(config_path: str = get_abs_path("config/chroma.yaml"), encoding: str = "utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


# 加载和prompts相关的配置文件
def load_prompts_config(config_path: str = get_abs_path("config/prompts.yaml"), encoding: str = "utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


# 加载和agent相关的配置文件
def load_agent_config(config_path: str = get_abs_path("config/agent.yaml"), encoding: str = "utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
prompts_conf = load_prompts_config()
agent_conf = load_agent_config()

if __name__ == '__main__':
    print(prompts_conf["main_prompt_path"])
