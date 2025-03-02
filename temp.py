def read_last_prompt(file_from):
    with open(file_from, 'r', encoding='utf-8') as file:
        # 读取整个文件内容
        content = file.read()
        
        # 从后向前查找最后一个 ``` 格式的标记
        last_prompt_index = content.rfind('```')
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

result = read_last_prompt("lang/prompt_zh.txt")
print(result)

def escape_json_string(json_string: str) -> str:
    return json_string.replace('&#44;', ',').replace('&amp;', '&').replace('&#91;', '[').replace('&#93;', ']')

# 示例用法
escaped_string = escape_json_string('{"app":"com.tencent.multimsg","config":{"autosize":1,"forward":1,"round":1,"type":"normal","width":300},"desc":"&#91;聊天记录&#93;","extra":"{\\"filename\\":\\"f66c0e6d-18c0-4cb9-9a40-a63426230439\\",\\"tsum\\":1}\\n","meta":{"detail":{"news":[{"text":"点击查看"}],"resid":"xMeL5CU/nTQ+0w5L8gTVS1ZTauyaWdb599SXe6XADRkjJ6jhLZRMeubYr4cCr6ks","source":"皇片","summary":"朕的皇欲又更新了","uniseq":"f66c0e6d-18c0-4cb9-9a40-a63426230439"}},"prompt":"&#91;聊天记录&#93;","ver":"0.0.0.5","view":"contact"}')
print(escaped_string)