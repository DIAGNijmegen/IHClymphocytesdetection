#!/bin/bash
#
set -e

mkdir -p "/home/user/data/tmp_input" 
mkdir -p "/home/user/data/tmp_masks"
mkdir -p "/home/user/data/tmp_output"
mkdir /output/images

echo "Processing all input files:"
ls /input

cp /input/*.tif /home/user/data/tmp_input

for file in /home/user/data/tmp_input/*.tif; do 
    filename=$(basename -- "$file")
    echo "Start processing: ${filename}"
    sh /home/user/run_source/process_single_image.sh "${file}" 

done

echo "Create result json file..."
python3.7 /home/user/run_source/create_json.py

cp /home/user/data/tmp_output/*.tif /output/images
cp /home/user/result.json /output/result.json

echo "Processing complete..."
exit 0
