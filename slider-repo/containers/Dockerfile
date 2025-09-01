# Developer container for Slider
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip llvm clang build-essential git && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY requirements.txt /work/requirements.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install -r /work/requirements.txt
ENV PATH="/opt/venv/bin:$PATH"
CMD ["/bin/bash"]
