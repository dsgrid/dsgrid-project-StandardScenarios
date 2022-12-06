# Dsgrid Contributors - Initial Directions for TEMPO & ResStock

## Step 0: Setup
1. If you do not have a python environment set up with python 3.8 or later, you may want to go ahead and set this up. 
2. Clone this Standard Scenarios dsgrid project repository.
3. Install dsgrid
    - Clone the [dsgrid repository](https://github.com/dsgrid/dsgrid).
    - Create a `dsgrid` clean environment: `conda create -n dsgrid python=3.8 pip`
    - Activate new `dsgrid` environment: `conda activate dsgrid`
    - Switch the branch to develop: `git checkout -b develop`
    - Pull in latest commits from develop: `git pull origin develop`
    - Install the development version of dsgrid (follow directions in the dsgrid README: `pip install -e '.[dev]'`
    - Note: dsgrid requires python=3.8 or later. If you do not already have a python environment with python>=3.8, then you will to get this set up. We recommend using [Anaconda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
4. Set up cloud access
    - You should already have access to the `nrel-aws-dsgrid` sandbox account. If you have not completed your account set up, you will want to do this. 
    - Log in and set up your password on the `nrel-aws-dsgrid` sandbox account (look for directions from Ricardo Oliveira in your email)
    - Make sure to set up MFA on this account (again, see email with instructions)
    - Download aws-cli if you do not already have it installed in your active conda environment: `pip install awscli`
    - Configure named profile for `nrel-aws-dsgrid`. See [these directions](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) for how to configure your named profile for the aws-cli. Or alternatively, follow these directions:
        ```
        vi ~/.aws/credentials
        ```
        Then add the following text (replacing XXXX with your creditentials):
        ```
        [nrel-aws-dsgrid]
        aws_access_key_id = XXXX
        aws_secret_access_key = XXXX
        ````
        Get your credentials from your AWS profile: https://console.aws.amazon.com/iam/home?#/security_credentials
        
    - Check that you can view contents in `s3://nrel-dsgrid-registry` bucket.

### Get familiar with the dsgrid cli
If you have dsgrid installed, you can spend a bit of time to get familiar with the dsgrid cli.

```dsgrid --help```

```
Usage: dsgrid [OPTIONS] COMMAND [ARGS]...

  dsgrid commands

Options:
  -l, --log-file PATH  Log to this file.
  -n, --no-prompts     Do not prompt.  [default: False]
  --verbose            Enable verbose log output.  [default: False]
  --help               Show this message and exit.

Commands:
  download  Download a dataset.
  query     Run a query on a dataset.
  registry  Manage a registry.
 ```

_NOTE: Both query and download are essentially inoperable right now._

- `dsgrid registry --help`
```
Usage: dsgrid registry [OPTIONS] COMMAND [ARGS]...

  Manage a registry.

Options:
  --path TEXT         path to dsgrid registry. Override with the environment
                      variable DSGRID_REGISTRY_PATH  [default:
                      /Users/mmooney/.dsgrid-registry]

  --remote-path TEXT  path to dsgrid remote registry  [default: s3://nrel-
                      dsgrid-registry]

  -o, --offline       run in registry commands in offline mode. WARNING: any
                      commands you perform in offline mode run the risk of
                      being out-of-sync with the latest dsgrid registry, and
                      any write commands will not be officially synced with
                      the remote registry

  -d, --dry-run       run registry commands in dry-run mode without writing to
                      the local or remote registry

  --help              Show this message and exit.

Commands:
  datasets            Dataset subcommands
  dimension-mappings  Dimension mapping subcommands
  dimensions          Dimension subcommands
  list                List the contents of a registry.
  projects            Project subcommands
  sync                Sync the official dsgrid registry to the local system.
```


## Step 1: Register dimensions
Create dimension csv files (in the project repository) and fill out the dimension.json5 file. Once you these are ready to go, we can register them.

Test it in dry run mode first:
```
dsgrid registry --dry-run dimensions register {path-to-dimension.json5} -l "{log message}"
```

If it worked, go ahead and register to AWS:
```
dsgrid registry --dry-run dimensions register {path-to-dimension.json5} -l "{log message}"
```

## Step 2: Update dataset.json5 with the dimension uuids and versions
The terminal will list out the registered dimensions. We will need to use these to pull out the version and dimension ID references. You can also see what dimensions are currently in the dsgrid registry by using the `dsgrid registry dimensions list` cli command.

Get the dimension ID and version information and update the dataset.json5 for each dimension.

## Step 3: Register dataset

```
dsgrid registry --offline datasets register {path-to-dataset.json5} -l "{log message}”
```


## Step 4: Generate dimension mappings (to map dataset to project)
If the dataset has different dimensions compared to the project, you will need to provide a dimension mapping back to the project before you can submit the dataset to the project. 

1. Create dimension mapping csvs + create the dimension_mappings.json5 file
2. Register via cli

```
dsgrid registry dimension-mappings register {path-to-dimension_mappings.json5} -l "{log message}”
```

## Step 4: Submit dataset to the project
Currently this is not ready yet, but it will be step 5 in this sequence.

1. Create a `dimension_mapping_references.json5` file
2. `dsgrid registry projects submit-dataset -d {dataset_id} -p {project_id} -l "{log message}"`
