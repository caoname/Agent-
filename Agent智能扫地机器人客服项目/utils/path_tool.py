"""
为整个工程提供统一的绝对路径
"""
import os


def get_project_root():
    """
    获取工程所在的根目录
    return字符串根目录
    """
    # 当前文件夹的绝对路径
    current_file = os.path.abspath(__file__)
    # print(f"current_file: {current_file}")
    # 先获取文件所在的文件夹绝对路径
    current_dir = os.path.dirname(current_file)
    # print(f"current-dir: {current_dir}")
    # 再获取工程根目录
    project_root = os.path.dirname(current_dir)
    # print(f"project root: {project_root}")
    return project_root


def get_abs_path(relative_path: str):
    """
    传递相对路径，得到绝对路径
    param relative_path：相对路径
    return 绝对路径
    """
    project_root = get_project_root()
    # print(relative_path)
    return os.path.join(project_root, relative_path)


if __name__ == '__main__':
    res = get_abs_path("config/config.txt")
    print(res)
