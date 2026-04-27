import os
from datetime import datetime
import uuid
class Saver:
    def __init__(self,folder_name):
        self.output_folder=folder_name
        os.makedirs(self.output_folder,exist_ok=True)


    def save_chat(self,messages:list[dict[str,str]],name:str=None):
        file_id=uuid.uuid4().hex[:6]
        if name is None:
            filename=f"chat_{file_id}_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.md"
        else:
            filename=f"{name}.md"
        file_path=os.path.join(self.output_folder,filename)
        with open(file_path,'w') as f:
            for message in messages:
                role = message.get("role")
                contect = message.get("message")
                if role == "user":
                    f.write(f"## User: {contect}\n\n")
                else:
                    f.write(f"## Assistant:\n {contect}\n\n")

        print(f"File saved in {file_path}")




