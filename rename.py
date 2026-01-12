import os
import re
import sys

def convert_obsidian_to_typora(directory, add_dot_slash=True):
    """
    遍历指定目录下所有 Markdown 文件，将 Obsidian 图片链接格式转换为 Typora Markdown 图片格式。

    Obsidian 格式:
        ![[image.png]]
        ![[folder/image.png]]
        ![[image.png|100]]
        ![[image.png|alt]]
        ![[image.png|100x200]]
    Typora 格式:
        ![](./image.png)
        ![](./folder/image.png)
    """

    # 支持常见图片扩展名
    image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp']

    # 说明：
    # !\[\[         : 匹配 "![["
    # (.*?)         : 捕获内部内容（包括 path + filename + 可选的 | 参数）
    # \]\]          : 匹配 "]]"
    #
    # 捕获后我们会再解析掉 | 后面的参数，只保留文件路径部分
    pattern_str = r'!\[\[(.*?)\]\]'
    obsidian_pattern = re.compile(pattern_str)

    # 用于判断是不是图片
    ext_pattern = re.compile(r'\.({})$'.format('|'.join(image_extensions)), re.IGNORECASE)

    def replacement(match):
        inner = match.group(1).strip()

        # 去掉 Obsidian 的 | 参数（如 |100 |alt |100x200 等）
        # Obsidian 的语法是 ![[file.png|something]]
        path_part = inner.split('|', 1)[0].strip()

        # 不是图片就不替换（比如 ![[note]]）
        if not ext_pattern.search(path_part):
            return match.group(0)

        # 是否补 ./ 前缀
        if add_dot_slash:
            # 如果已经是相对路径 (./ 或 ../) 或绝对路径（/）或 URL，就不加
            if not (path_part.startswith("./") or path_part.startswith("../") or path_part.startswith("/") or "://" in path_part):
                path_part = "./" + path_part

        return f"![]({path_part})"

    # 遍历目录
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    new_content, num_replacements = obsidian_pattern.subn(replacement, content)

                    if num_replacements > 0 and new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)

                        print(f"处理文件: {file_path}")
                        print(f"  -> 成功转换 {num_replacements} 个链接。")

                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}", file=sys.stderr)

    print("\n所有文件处理完毕！")


if __name__ == '__main__':
    target_directory = input("请输入您的笔记库文件夹的绝对路径: ")

    if os.path.isdir(target_directory):
        # add_dot_slash=True: 输出 ![](./xxx.png)
        # add_dot_slash=False: 输出 ![](xxx.png)
        convert_obsidian_to_typora(target_directory, add_dot_slash=True)
    else:
        print("错误: 您输入的不是一个有效的文件夹路径。", file=sys.stderr)
