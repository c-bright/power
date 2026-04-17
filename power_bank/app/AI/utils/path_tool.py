
import os

def get_project_root():
    """
    获取项目根目录（基于当前文件路径）
    """
    # 当前文件所在目录
    current_path = os.path.abspath(__file__)
    # 向上两级
    project_root = os.path.dirname(os.path.dirname(current_path))

    return project_root


def build_path(*paths):
    """
    拼接路径，返回完整路径
    :param paths: 可变参数，例如 ('data', 'test.txt')
    """
    root = get_project_root()
    return os.path.join(root, *paths)


if __name__ == "__main__":

    print(build_path("data.scs"))
    print(build_path("data\prompt_template.txt"))