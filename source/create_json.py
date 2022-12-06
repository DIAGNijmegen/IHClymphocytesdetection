import os 
import json
import glob 

output = list() 

input_files = glob.glob("/input/*.*")
result_base_path = "/home/user/data/tmp_output" 

for file in input_files:
    filename = os.path.splitext(os.path.basename(file))[0]
    output_file_path = os.path.join(result_base_path, filename + '.tif')
    output_file_name = filename

    if os.path.isfile(output_file_path):
        entry = {
                "entity": file,
                "output": f"filepath:images/fixed-mask/{output_file_name}",
                "error_messages": [],
                "metrics": {"f1": "N/A"},
                }

        output.append(entry)

with open("/home/user/result.json", "w") as file:
    json.dump(output, file, indent=4)

