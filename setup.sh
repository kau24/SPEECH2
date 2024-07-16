#!/bin/sh
# Download and install ffmpeg
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz | tar xJ
export PATH=$PATH:$PWD/ffmpeg-*-static
