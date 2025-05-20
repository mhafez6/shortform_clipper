import glob
import json
import os
import pathlib
import pickle
import shutil
import subprocess
import time
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import modal
import boto3
import whisperx
from pydantic import BaseModel
from google import genai



class ProcessVideoRequest(BaseModel):
    s3_key: str

# -- modal docker image config -- 
image = (modal.Image.from_registry( 
    "nvidia/cuda:12.4.0-devel-ubuntu22.04", add_python='3.12')
    .apt_install(["ffmpeg", "libgl1-mesa-glx", "wget", "libcudnn8", "libcudnn8-dev"])
    .pip_install_from_requirements("requirements.txt")
    .run_commands(["mkdir -p /user/share/fonts/truetype/custom",
                   "wget -O /user/share/fonts/truetype/custom/Anton-Regular.ttf https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
                   "fc-cache -f -v"])
    .add_local_dir("asd", "/asd", copy=True))



app = modal.App("ai-podcast-clipper", image=image)

# create a volume which will allow us to add a "hard drive" where we can access files that are saved accross diff images
volume = modal.Volume.from_name(
    "ai-podcast-clipper-model-cache", create_if_missing=True
)

mount_path = "/root/.cache/torch"

auth_scheme=HTTPBearer()


def create_vertical_video(tracks, scores, pyframes_path, pyavi_path, audio_path, output_path, framerate=25):
    target_width=1080
    target_height=1920

    flist = glob.glob(os.path.join(pyframes_path, "*jpg"))
    flist.sort()

def process_clip(base_dir: str, original_video_path: str, s3_key:str, start_time: float, end_time: float, clip_index: int, transcript_segments: list):
    clip_name = f"clip_{clip_index}"
    s3_key_dir = os.path.dirname(s3_key)
    output_s3_key = f"{s3_key_dir}/{clip_name}.mp4"
    print(f"Output s3 key {output_s3_key}")

    clip_dir = base_dir / clip_name
    clip_dir.mkdir(parents=True, exist_ok=True)

    # segment path: original clip from start to end point of the og video
    clip_segment_path = clip_dir / f"{clip_name}_segment.mp4"
    # vertical cut clip 
    vertical_mp4_path = clip_dir / "pyavi" / "video_out_verical.mp4"
    #verical clip with subtitles
    subtitle_output_path = clip_dir / "pyavi" / "video_with_subtitles.mp4"

    #create dirs for the asd model 
    (clip_dir / "pywork").mkdir(exist_ok=True)
    pyframes_path = clip_dir / "pyframes"
    pyavi_path = clip_dir / "pyavi"
    audio_path = clip_dir / "pyavi" / "audio.wav"

    pyframes_path.mkdir(exist_ok=True)
    pyavi_path.mkdir(exist_ok=True)

    duration = end_time - start_time
    cut_cmd = (f"ffmpeg -i {original_video_path} --ss {start_time} -to {duration} {clip_segment_path}")

    subprocess.run(cut_cmd, shell=True, check=True, capture_output=True, text=True)

    extract_audio_cmd = f"ffmpeg -i {clip_segment_path} -vn -acodec pcm-s16le -ar 16000 -ac 1 {audio_path}"
    subprocess.run(extract_audio_cmd, shell=True, check=True, capture_output=True, text=True)

    shutil.copy(clip_segment_path, base_dir / f"{clip_name}.mp4")

    columbia_cmd = (f"python Columbia_test.py --videoName {clip_name} "
                    f"--videoFolder {str(base_dir)}"
                    f"--pretrainModel weight/finetuning_TalkSet.model")
    
    columbia_starttime= time.time()
    subprocess.run(columbia_cmd, cwd="/asd", shell=True, )
    columbia_endtime= time.time()
    print(f"asd columbia takes {columbia_endtime-columbia_starttime} seconds" )

    tracks_path = clip_dir / "pywork" / "tracks.pckl"
    scores_path = clip_dir / "pywork" / "scores.pckl"

    if not tracks_path.exists() or not scores_path.exists():
        raise FileNotFoundError("tracks or scores not found for clipping")

    with open(tracks_path, "rb") as f:
        tracks = pickle.load(f)
    with open(scores_path, "rb") as f:
        scores = pickle.load(f)

    cvv_starttime= time.time()
    
    create_vertical_video(
        tracks, scores, pyframes_path, pyavi_path, audio_path, vertical_mp4_path
    )

    cvv_endtime= time.time()
    print(f" cvv takes {cvv_endtime-cvv_starttime} seconds" )





@app.cls(gpu="L40S", timeout=900, retries=0, scaledown_window=20, secrets=[modal.Secret.from_name('ai-podcast-clipper-secret')], volumes={mount_path: volume})
class AiPodcastClipper:
    @modal.enter()
    def load_model(self):
        print("loading models")

        self.whisperx_model = whisperx.load_model("large-v2", device="cuda", compute_type="float16")
        self.alignment_model, self.metadata = whisperx.load_align_model(language_code="en", device="cuda")

        print('transcription models loaded')

        print("geminin client creation..")
        self.gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        print("geminin client creation done")



    def transcribe_video(self, base_dir:str, video_path: str) -> str:

        audio_path = base_dir / "audio.wav"
        extract_cmd= f"ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar 16000 -ac 1 {audio_path}"
        subprocess.run(extract_cmd, shell=True, check=True, capture_output=True)

        print("Starting transcription with Whisperx...")
        start_time=time.time()

        audio = whisperx.load_audio(str(audio_path))
        result = self.whisperx_model.transcribe(audio, batch_size=16)

        result = whisperx.align(
            result["segments"],
            self.alignment_model,
            self.metadata,
            audio,
            device='cuda',
            return_char_alignments=False
        )

        duration = time.time() - start_time

        print('Transcription and allignment took' + str(duration) + " seconds")
        
        segments = []

        if "word_segments" in result:
            for word_segment in result['word_segments']:
                segments.append({
                    "start": word_segment['start'],
                    "end": word_segment['end'],
                    "word": word_segment['word'],
                })

        return json.dumps(segments)

    
    def identify_moments(self, transcript: dict):
        response = self.gemini_client.models.generate_content(model="gemini-2.5-flash-preview-04-17", contents="""
        This is a podcast video transcript consisting of word, along with each words's start and end time. I am looking to create clips between a minimum of 30 and maximum of 60 seconds long. The clip should never exceed 60 seconds.

    Your task is to find and extract stories, or question and their corresponding answers from the transcript.
    Each clip should begin with the question and conclude with the answer.
    It is acceptable for the clip to include a few additional sentences before a question if it aids in contextualizing the question.

    Please adhere to the following rules:
    - Ensure that clips do not overlap with one another.
    - Start and end timestamps of the clips should align perfectly with the sentence boundaries in the transcript.
    - Only use the start and end timestamps provided in the input. modifying timestamps is not allowed.
    - Format the output as a list of JSON objects, each representing a clip with 'start' and 'end' timestamps: [{"start": seconds, "end": seconds}, ...clip2, clip3]. The output should always be readable by the python json.loads function.
    - Aim to generate longer clips between 40-60 seconds, and ensure to include as much content from the context as viable.

    Avoid including:
    - Moments of greeting, thanking, or saying goodbye.
    - Non-question and answer interactions.

    If there are no valid clips to extract, the output should be an empty list [], in JSON format. Also readable by json.loads() in Python.

    The transcript is as follows:\n\n
""" + str(transcript))
        print(f"Identified moments response: {response.text}")
        return response.text
    

    @modal.fastapi_endpoint(method="POST")
    def process_video(self, request: ProcessVideoRequest, token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
        
        s3_key = request.s3_key

        if token.credentials != os.environ["AUTH_TOKEN"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inccorrect bearer tokenn", headers={"WWW-Authneticate": "Bearer"})

        run_id = str(uuid.uuid4())
        base_dir= pathlib.Path("/tmp") / run_id
        base_dir.mkdir(parents=True, exist_ok=True)

        # Downlaod video file
        video_path = base_dir / "input.mp4"
        s3_client = boto3.client("s3")
        s3_client.download_file("shortform-clipper", s3_key, str(video_path))

        # 1.  this is getting transcription 
        transcripts_segments_json = self.transcribe_video(base_dir, video_path)
        transcripts_segments = json.loads(transcripts_segments_json)

        # 2. get clip moments
        print('identifying clip moments')
        identified_moments_raw = self.identify_moments(transcripts_segments)
        cleaned_json_string = identified_moments_raw.strip()
        if cleaned_json_string.startswith("```json"):
            cleaned_json_string = cleaned_json_string[len("```json"):].strip()
        if cleaned_json_string.endswith("```"):
            cleaned_json_string = cleaned_json_string[:-len("```")].strip()

        clip_moments = json.loads(cleaned_json_string)
        if not clip_moments or isinstance(clip_moments, list):
            print("Erorr: clip moments isn't a list")
            clip_moments = []

        print(clip_moments)

        # 3. processing clips
        for index, moment in enumerate(clip_moments[:2]):
            if "start" in moment and "end" in moment:
                print("processing clip" + str(index) + " from" + str(moment['start']) + "tp " + str(moment['end']))

            process_clip(base_dir, video_path, s3_key, moment["start"], moment["end"], index, transcripts_segments)


        if base_dir.exists():
            print("Cleaing up temp dir after " + base_dir)
            shutil.rmtree(base_dir, ignore_errors=True)




@app.local_entrypoint()
def main():
    import requests

    ai_podcast_clipper=AiPodcastClipper() # we're creating an instance of the above class
    url = ai_podcast_clipper.process_video.web_url # getting url that's defined by decorator

    payload = {
        's3_key': 'test1/445min.mp4'
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 123123"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    print(result)