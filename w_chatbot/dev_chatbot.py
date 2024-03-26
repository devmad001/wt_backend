Recall yours:
 
    C:\scripts-22\chatgpt\chatgpt_api


    ## REDO SPECIFICALLY FOR .sh
    
    caps=[]
    caps+=[('lost_mount','Reboot lost','sudo mount /dev/nvme1n1 /data')]
    caps+=[('ENV','OpenAI Key','cd /home/ubuntu/chatskit && source ./SETUPENV.sh')]
    caps+=[('weaviate','Vector database on 8080','cd /home/ubuntu/weaviate && sudo nohup docker-compose up > nohup_weav.out & ')]
    caps+=[('upload','Upload endpoint w bottle on 8081; upload.chatskit.com/project/buildingscience','cd /home/ubuntu/chatskit/chat_apis/storage_api && nohup python pyfiledrop.py > nohup_upload.out & ')]
    caps+=[('streamlit_chat_ui','Run via streamlit module port 8082','cd /home/ubuntu/chatskit/chatskit_ui && nohup python -m streamlit run example_chatbot.py --server.port 8082 > nohup_chat.out &')]
    caps+=[('flask_model','Huggingface model + model port 5005; ask.chatskit.com/buildingscience?query=ok question','cd /home/ubuntu/chatskiti && nohup python flask_chat.py > nohup_flask_chat.out &')]
    
    for topic,note,cmd in caps:
        print ("RUN> "+str(cmd))

