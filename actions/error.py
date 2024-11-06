from discord import *


def get_error(error:str):
    embed = Embed(title="❌Hum... Seems like some error occurred❌",description="❌嗯... 看起來出了點錯❌",color=0xff0000)
    if "Command" in error and "is not found" in error:
        error_type = "unknown command 未知的指令"
    elif "Missing Permissions" in error:
        error_type = "no permission 權限錯誤"
    else:
        error_type = "Unknown error 未知的錯誤"

    embed.add_field(name="Type",value=error_type)
    return embed

def no_permission(text:str):
    embed = Embed(title=text,color=0x00ff00)
    return embed