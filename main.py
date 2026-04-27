#! /usr/bin/env python3
from rag_pipeline import RagPipeline
import sys
from ragcore.exceptions import BotRagException

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 main.py <persist_dir> <output_folder>")
        sys.exit(1)

    rag = RagPipeline(sys.argv[1],sys.argv[2])
    chat_history=[]
    try:
        source_id=None

        mode=input("Choose mode:\n1. Process file\n2. Youtube video\n> ").strip()
        if mode == "2":
            url=input("Enter youtube url: ")
            source_id=rag.ingest_video(url)
        else:
            source_id=rag.ingest("./files")
    except BotRagException as e:
        print(f"Error: {e}")

    if input("Choose mode:\n1. Write \n2. Speak\n >").strip() == '1':
        while True:
            query=input("Enter question: ")
            if query.lower() in ('exit','quit','q'):
                break
            ans=rag.ask(question=query,source_id=source_id,chat_history=chat_history)
            print(ans)
            chat_history.append({"role":"user","message":query})
            chat_history.append({"role":"assistant","message":ans})
    else:
        while True:
            query=rag.hear()
            if query is None:
                print("No input detected. Please try again.")
                continue
            if query.lower() in ('exit','quit','q'):
                break
            ans=rag.ask(question=query,source_id=source_id,chat_history=chat_history)
            rag.say(ans)
            chat_history.append({"role":"user","message":query})
            chat_history.append({"role":"assistant","message":ans})
    if input("Do you want to save the output? (y/n)").strip().lower() == 'y':
        rag.save(chat_history)
