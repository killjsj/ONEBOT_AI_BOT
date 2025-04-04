messages = [{"role": "system", "content": "你是一个AI助手，帮助用户解决问题。"}]
picture = ""
input = "你能帮我画一只猫吗？"
if messages[0]["role"] == "system":
            messages[0]["role"] = "user"
            if len(messages)==1:
                messages[0]["content"] += " | "  + input
            else:
                messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": input}, {"type": "image_uri", "image_uri": picture}] if picture != "" else [{"type": "text", "text": input}],
                })
else:
            messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": input}, {"type": "image_uri", "image_uri": picture}] if picture != "" else [{"type": "text", "text": input}],
                })
print(messages)