from pathlib import Path

import json5
import pandas as pd

dataset_path = Path(__file__).absolute().parent.parent
dim_path = dataset_path / "dimensions"
project_path = dataset_path.parent

tempo_bins = pd.read_csv(dim_path / "bin.csv")["id"].to_frame()
print(tempo_bins)

for filepath in (dim_path / "supplemental").glob("*.csv"):
    subset_dim_name = filepath.stem
    df = tempo_bins.copy()
    p = project_path / "dimensions" / "subset" / f"{subset_dim_name}.csv"
    config = dict(name=subset_dim_name,
                  description="",
                  type="subset",
                  filename=str(p.relative_to(project_path)),
                  selectors=[])
    subsets = pd.read_csv(filepath)
    for id, name in subsets.itertuples(index=False):
        df[id] = df["id"].apply(lambda x: "x" if id in x else "")
        config["selectors"].append(dict(name=id, description=name))

    df.to_csv(p,index=False)
    print(json5.dumps(config,indent=2))
