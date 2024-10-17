
def readprompt(file_from:str,target:str):
    target = str(target)
    with open(file_from,'r') as file:
        #check
        prompt_list = file.readlines()
        for a in prompt_list:
            a = a.strip()
        if prompt_list[0][:2] != '```0':
            raise TypeError('prompt not correct format')
        
