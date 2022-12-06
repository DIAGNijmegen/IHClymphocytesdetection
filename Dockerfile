FROM doduo1.umcn.nl/johnmelle/base_docker_cuda_10:5

COPY models /home/user/models
COPY source /home/user/run_source

USER user
WORKDIR /home/user

ENTRYPOINT ["/bin/bash", "/home/user/run_source/start_processing.sh"]

COPY torch_processor.py to /home/user/source/pathology-fast-inference/fastinference/processors/torch_processor.py

# Compute requirements for the processor
LABEL processor.cpus="8"
LABEL processor.cpu.capabilities="null"
LABEL processor.memory="25G"
LABEL processor.gpu_count="1"
LABEL processor.gpu.compute_capability="null"
LABEL processor.gpu.memory="8G"
