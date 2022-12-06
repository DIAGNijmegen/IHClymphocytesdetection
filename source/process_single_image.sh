#!/bin/bash

export 'TF_CPP_MIN_LOG_LEVEL'='3'
export TF_CPP_MIN_LOG_LEVEL=3

image_to_process=$1

filename=$(basename -- "$image_to_process")

temp_output_something=/home/user/data/tmp_output/${filename%.*}.tif

# echo "Create tissue-background mask..."
# python3.7 /home/user/source/pathology-fast-inference/scripts/applynetwork_multiproc.py \
# --input_wsi_path="${image_to_process}" \
# --output_wsi_path="${output_bg}" \
# --model_path="/home/user/models/tissue_background.net" \
# --read_spacing=1.0 \
# --write_spacing=1.0 \
# --tile_size=512 \
# --readers=4 \
# --writers=4 \
# --batch_size=10 \
# --gpu_count=1 \
# --unfix_network \
# --quantize
#
# echo "Normalize mask..."
# python3.7 /home/user/source/pathology-common/scripts/maplabels.py \
# --input=${output_bg} \
# --output=${output_bg_norm} \
# --map="{1:0,2:1}"

echo "Apply segmentation network..."
# python3.7 /home/user/source/pathology-fast-inference/scripts/applynetwork_multiproc.py \
# --input_wsi_path="${image_to_process}" \
# --output_wsi_path="/home/user/data/tmp_output/{image}.tif" \
# --model_path="/home/user/models/model19.pt" \
# --read_spacing=1.0 \
# --write_spacing=1.0 \
# --tile_size=64 \
# --readers=4 \
# --writers=4 \
# --batch_size=64 \
# --axes_order='cwh' \
# --custom_processor="torch_processor" \
# --reconstruction_information="[[0,0,0,0],[1,1],[16,16,16,16]]" \
# --gpu_count=1 \
# --soft \
# --quantize

python3.7 /home/user/source/pathology-fast-inference/scripts/applynetwork_multiproc.py \
--model_path="/home/user/models/lymphocyte_fcn.net" \
--input_wsi_path="${image_to_process}" \
--output_wsi_path="/home/user/data/tmp_output/{image}.tif" \
--tile_size=1024 \
--read_spacing=0.25 \
--write_spacing=2.0 \
--gpu_count=1 \
--batch_size=8 \
--readers=4 \
--writers=4 \
--work_directory="/home/user/work" \
--cache_directory="/home/user/cache" \
--normalizer="default" \
--soft \
--quantize

python3.7 /home/user/source/postprocessing.py \
--input_wsi_path="${temp_output_something}" \
--output_path="/home/user/data/tmp_output/{image}.tif" \
