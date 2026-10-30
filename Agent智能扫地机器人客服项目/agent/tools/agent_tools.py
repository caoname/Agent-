import os
import random

from langchain_core.tools import tool
from utils.logger_handler import logger
from rag.rag_service import RagSummarizeService
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path

rag = RagSummarizeService()

user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]
month_arr = ["2025-01", "2025-02", "2025-04", "2025-05", "2025-06", "2025-07", "2025-03",
             "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"]


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city: str) -> str:
    return f"城市{city}的天气为晴天，气温26度，空气湿度50%，南风一级，AQI21，最近六小时降雨概率极低"


@tool(description="获取用户所在地的城市名称，以纯字符串形式返回")
def get_user_location() -> str:
    return random.choice(["深圳", "合肥", "杭州"])


@tool(description="获取用户ID，以纯字符串格式返回")
def get_user_id() -> str:
    return random.choice(user_ids)


@tool(description="获取当前月份，以纯字符串格式返回")
def get_current_month() -> str:
    return random.choice(month_arr)


"""
就剩下获取外部数据这个工具了，因为用户如果要它的使用报告，我们需要知道它的使用行为，而使用行为就在external中的
records.csv中，因此需要一个外部工具来获取到这些原始信息
"""
external_data = {}


# 从文件中把数据都读取到，组装成字典返回，方便读取。为了避免臃肿所以不跟下一个方法合并
# 做的就是把csv内容取到转成字典
def generate_external_data():
    """
    {
        "user_id": {
                "month":{"特征":XXX,"清洁效率":XXXX,"耗材":XXXX,....},
                "month":{"特征":XXX,"清洁效率":XXXX,"耗材":XXXX,....},
                "month":{"特征":XXX,"清洁效率":XXXX,"耗材":XXXX,....},
        },
        "user_id": {
                "month":{"特征":XXX,"清洁效率":XXXX,"耗材":XXXX,....},
                "month":{"特征":XXX,"清洁效率":XXXX,"耗材":XXXX,....},
                "month":{"特征":XXX,"清洁效率":XXXX,"耗材":XXXX,....},
        },
        "user_id": {
                "month":{"特征":XXX,"清洁效率":XXXX,"耗材":XXXX,....},
                "month":{"特征":XXX,"清洁效率":XXXX,"耗材":XXXX,....},
                "month":{"特征":XXX,"清洁效率":XXXX,"耗材":XXXX,....},
        },
        ......
    结构大概是这样，比如userX的X月份的某个数据
    }
    """
    # 字典第一次进来是空的才填充，这样把内容全填进去后面就不需要每次都调用进行填充
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")

        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:      # 从数据的第二行开始取，不包括第一行，第一行是表头
                arr: list[str] = line.strip().split(",")    # 数据是通过,分隔的，就按逗号切分,每一行都变成list

                # 把双引号都替换成空字符串，也就是把双引号删掉.下面每一行都是表头的一个元素
                # "用户ID","特征","清洁效率","耗材","对比","时间"
                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")
                # 上面就完成了把一行里面的所有字典都拿到了

                # 如果当前的user_id并不存在在external_data，就往里加信息（因为external_data一开始是空字典）
                if user_id not in external_data:
                    # 因为一开始字典为空，所以现在按照不同用户把其对应的数据存到字典当中
                    external_data[user_id] = {}

                # 这里的time是获取文件中的具体时间的，也就是一开始注释中的month
                external_data[user_id][time] = {
                    "特征": feature,
                    "清洁效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }
                # 至此这个字典就构造完了


@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式返回，如果为检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()

    try:        # 获取到信息就直接返回
        return external_data[user_id][month]
    except KeyError:
        logger.error(f"[fetch_external_data]未能检索到用户：{user_id}在{month}的使用记录")
        return ""


@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"

# if __name__ == '__main__':
#     # 只有注释调fetch_external_data上面的工具才能运行
#     print(fetch_external_data("1021", "2025-11"))
