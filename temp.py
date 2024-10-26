import os

def readprompt(file_from: str, target_i: int = 0):
    with open(file_from, 'r', encoding='utf-8') as file:
        prompt_list = file.readlines()
        if prompt_list[0][:4] != '```0':
            raise TypeError('prompt not correct format')
        # format check
        target = '```' + str(target_i)
        finall = ''
        check_p1 = False
        for a in prompt_list:
            a = a.strip()
            if check_p1:
                if a[:3 + len(str(int(target_i) + 1))] == ('```' + str(int(target_i) + 1)) or a[:3 + len(str(int(target_i) + 1))] == "```":
                    finall = finall.strip('\n')
                    return finall
                finall += a + '\n'
            if a[:3 + len(str(target_i))] == target:
                check_p1 = True
            print(a[:3 + len(str(int(target_i) + 1))])
        return None

langprom = os.path.join('lang', 'prompt_zh.txt')
print(readprompt(langprom, 1))