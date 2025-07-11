# NVIDIA Maxine NIM

NVIDIA Maxine is a suite of high-performance, easy-to-use, NVIDIA Inference Microservices (NIMs) for deploying AI features that enhance audio, video, and augmented reality effects for video conferencing and tele-presence.


## NVIDIA Maxine NIM Clients

This repository provides sample client applications to interact with Maxine NIMs

- [`eye-contact`](eye-contact) - NVIDIA Maxine Eye Contact feature estimates the gaze angles of a person in a video and redirects the gaze in the output video to make it frontal.
[[Demo](https://build.nvidia.com/nvidia/eyecontact)] , [[Docs](https://docs.nvidia.com/nim/maxine/eye-contact/latest/index.html)]

- [`studio-voice`](studio-voice) - NVIDIA Maxine Studio Voice feature enhances the input speech recorded through low quality microphones in noisy and reverberant environments to studio-recorded quality speech.
[[Demo](https://build.nvidia.com/nvidia/studiovoice)] , [[Docs](https://docs.nvidia.com/nim/maxine/studio-voice/latest/index.html)]

- [`audio2face-2d`](audio2face-2d) - NVIDIA Maxine Audio2Face-2D feature generates facial animations from a portrait photo and audio input, synchronizing mouth movements with speech to create realistic and engaging video outputs.
[[Demo](https://build.nvidia.com/nvidia/audio2face-2d)] , [[Docs](https://docs.nvidia.com/nim/maxine/audio2face-2d/latest/index.html)]

podman run -it --name=studio-voice \
    --device nvidia.com/gpu=all \
    --shm-size=8GB \
    -e NGC_API_KEY=$NGC_API_KEY \
    -e FILE_SIZE_LIMIT=36700160 \
    -e STREAMING=false \
    -p 8000:8000 \
    -p 8001:8001 \
    nvcr.io/nim/nvidia/maxine-studio-voice:latest