import os

def check(id:str|int) -> bool:
    if os.path.exists(f"./userdatas/{id}.json"):
        return False # not new
    return True # is new