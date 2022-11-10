from pathlib import Path 
import json5
import toml
import glob
from dsgrid.data_models import ExtendedJSONEncoder
from itertools import groupby
from operator import itemgetter

project_dir = Path().absolute() / "dsgrid_project"

def convert_toml_to_json(toml_file, write=True):
    json5_file = str(toml_file).replace(".toml", ".json5")
    toml_config = toml.load(toml_file)
    json5_config = json5.dumps(toml_config, indent=2, cls=ExtendedJSONEncoder)
    if write:
        with open(json5_file, 'w') as f:
            f.write(json5_config) 

def check_toml_comments(toml_file):
    json5_file = str(toml_file).replace(".toml", ".json5")
    with open(toml_file, "r+") as f:
        storagearray = []
        read_lines = f.readlines()
        # find blocks of comments
        comment_lines = []
        for i, line in enumerate(read_lines):
            if line.startswith("#"):
                comment_lines.append(i)
        # print(comment_lines)
        
        for k, g in groupby(enumerate(comment_lines), lambda ix : ix[0] - ix[1]):
            for comment_id_block in [list(map(itemgetter(1), g))]:
                if len(comment_id_block) > 1:
                    # print(comment_id_block, comment_id_block[0], comment_id_block[-1])
                    comment_block  = read_lines[comment_id_block[0]:comment_id_block[-1]+1]
                    if comment_block[0].startswith("# ---") and comment_block[-1].startswith("# ---"):
                        pass
                    else:
                        print(comment_block) 
                    # ignore blocks that are just section headers, e.g. ----- ...

        
        # for i, line in enumerate(read_lines):
        #     if line.startswith("#"):
        #         if "todo" in line.lower():
        #             print(i, line)
        #             # TODO do something with todos
        #         # print(i, line, read_lines[i+1])
        #         pass
        #     elif "#" in line:
        #         if "todo" in line.lower():
        #             print(i, line)
        #             # TODO do something with todos
        #         # print(i, line)
        #         # print(line.split("#")[0])
        #         # find the placement in the json file
        #         # replace_in_json()
    print(storagearray)

           

# project toml
toml_file = project_dir / "project.toml"
convert_toml_to_json(toml_file, write=True)
# check_toml_comments(toml_file)
    
# dataset toml files (*/dataset.toml, */dimension_mappings.toml)
for dataset_type in ("historical", "modeled"):
    dataset_group_dir = project_dir / "datasets" / dataset_type
    for dataset_dir in dataset_group_dir.iterdir():
        for toml_file in list(dataset_dir.glob('**/*.toml')):
            convert_toml_to_json(toml_file, write=True)



# Check to make sure, at minimum, all TODO comments are captured

# Check to make sure blocks of comments are captured