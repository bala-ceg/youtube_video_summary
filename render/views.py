from django.shortcuts import render

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
import mindsdb_sdk as mdb
import pandas as pd
import json

from dotenv import load_dotenv
load_dotenv()
import os


from render.models import video_sum_predicted

def home(request):
    return render(request,'home.html')

def yt_show(request):

    if request.method == 'POST':
        yt_video_url = request.POST['yt_url']
    
    print(yt_video_url)
    match = re.search(r"v=([A-Za-z0-9_-]+)", yt_video_url)

    if match:
        video_id = match.group(1)
        print(video_id)
        videos = video_sum_predicted.objects.filter(video_id=video_id).values()
        print(videos)
        if videos.exists():
            video = videos[0]
            status_response = json.dumps({'summary': video['summary'],'video_id': video['video_id']})
            status_response_json = json.loads(status_response)
            return render(request,'ytshow.html',{'status':status_response_json})

    else:
        status_response  =json.dumps({'error_message': 'Youtube Video ID Not Found. Please copy & paste the correct Youtube url'})
        status_response_json = json.loads(status_response) 
        return render(request,'yt_video_validation.html',{'status':status_response_json})


    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        status_response  =json.dumps({'error_message': 'Transcription for the given video is not available in the youtube. Please try a different video url.'})
        status_response_json = json.loads(status_response) 
        return render(request,'yt_video_validation.html',{'status':status_response_json})

    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)

    with open('transcript.txt', 'w', encoding='utf-8') as txt_file:
        txt_file.write(text_formatted)
    
    with open('transcript.txt', 'r') as f:
        lines = f.readlines()

    df = pd.DataFrame({'transcript': [lines]})
    print(df)

    MDB_EMAIL =  os.environ.get("MINDSDB_USERNAME")
    MDB_PWD = os.environ.get("MINDSDB_PASSWORD")
    MODEL_NAME = os.environ.get("MINDSDB_MODEL")

    server=mdb.connect(login=MDB_EMAIL,password=MDB_PWD)
    model=server.get_project('mindsdb').get_model(MODEL_NAME)
    print(model)
    try: 
        pred_df=model.predict(df)
        print(pred_df)
    except Exception as e:
        status_response  =json.dumps({'error_message': 'Something is wrong with this video. Please try pasting a different video'})
        status_response_json = json.loads(status_response) 
        return render(request,'yt_video_validation.html',{'status':status_response_json})
   

    pred_df.to_csv('output.txt', index=False, header=False, sep=' ')

    with open('output.txt', 'r') as f:
        contents = f.read()

    status_response  =json.dumps({'summary': contents,'video_id': video_id})
    status_response_json = json.loads(status_response) 

    p = video_sum_predicted(summary=contents,video_id=video_id)
    p.save()


    return render(request,'ytshow.html',{'status':status_response_json})
