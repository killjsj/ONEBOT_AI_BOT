def read_last_prompt(file_from):
    with open(file_from, 'r', encoding='utf-8') as file:
        # 读取整个文件内容
        content = file.read()
        
        # 从后向前查找最后一个 ```数字``` 格式的标记
        last_prompt_index = content.rfind('```',0,len(content[:-3]))
        if last_prompt_index == -1:
            raise TypeError('No prompt found in the file')
        
        # 提取最后一个标记的内容
        last_prompt = content[last_prompt_index:]
        
        # 提取最后一个标记的数字
        # 假设标记格式为 ```数字```，且数字可能有多位
        import re
        match = re.search(r'```(\d+)', last_prompt)
        if not match:
            raise TypeError('No valid prompt number found in the last prompt')
        
        last_prompt_number = match.group(1)
        
        return last_prompt_number
result = read_last_prompt("lang\prompt_zh.txt")
print(result)