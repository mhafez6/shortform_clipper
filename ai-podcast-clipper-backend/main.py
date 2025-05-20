from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import modal
from pydantic import BaseModel

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


@app.cls(gpu="L40S", timeout=900, retries=0, scaledown_window=20, secrets=[modal.Secret.from_name('ai-podcast-clipper-secret')], volumes={mount_path: volume})
class AiPodcastClipper:
    @modal.enter()
    def load_model(self):
        print("loading models")
        pass
    
    @modal.fastapi_endpoint(method="POST")
    def process_video(self, request: ProcessVideoRequest, token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
        print("Processing video " + request.s3_key)
        pass

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