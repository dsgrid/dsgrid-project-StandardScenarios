# Dsgrid Contributors - Initial Directions for TEMPO

Setup:
- install dsgrid --> clone the dsgrid repository. Switch the branch to develop. Follow the directions in the README to `pip install -e '.[dev]'`
- check that you can access the `nrel-aws-dsgrid` cloud account; check that you can view contents in `s3://nrel-dsgrid-registry` bucket.
- You will need to make sure you have the `nrel-aws-dsgrid` profile name in your aws configure file. Directions to set this up are here: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html
- get familiar with the dsgrid cli
	- `dsgrid registry --help`
	- `dsgrid registry —offline` : allows you to work in offline mode (i.e., doesn’t constantly sync data, allows you to “work offline” from the AWS dsgrid registry)
	- `dsgrid registry —dry-run`: allows you test your registry commands without making any official changes to the remote AWS registry


## Step 1: Register dimensions
Create dimension csv files (in the project repository) and fill out the dimension.toml file. Once you these are ready to go, we can register them.

Test it in dry run mode first:
```
dsgrid registry --dry-run dimension-mappings register {path-to-dimension.toml} -l "{log message}"
```

If it worked, go ahead and register to AWS:
```
dsgrid registry --dry-run dimension-mappings register {path-to-dimension.toml} -l "{log message}"
```

## Step 2: Update dataset.toml with the dimension uuids and versions
The terminal will list out the registered dimensions. We will need to use these to pull out the version and dimension ID references. You can also see what dimensions are currently in the dsgrid registry by using the `dsgrid registry dimensions list` cli command.

Get the dimension ID and version information and update the dataset.toml for each dimension.

## Step 3: Register dataset

```
dsgrid registry --offline datasets register {path-to-dataset.toml} -l "{log message}”
```


## Step 4: Generate dimension mappings (to map dataset to project)
If the dataset has different dimensions compared to the project, you will need to provide a dimension mapping back to the project before you can submit the dataset to the project. 

1. Create dimension mapping csvs + create the dimension_mappings.toml file
2. Register via cli

```
dsgrid registry dimension-mappings register {path-to-dimension_mappings.toml} -l "{log message}”
```

## Step 4: Submit dataset to the project
Currently this is not ready yet, but it will be step 5 in this sequence.

1. Create a `dimension_mapping_references.toml` file
2. `dsgrid registry projects submit-dataset -d {dataset_id} -p {project_id} -l "{log message}"`
