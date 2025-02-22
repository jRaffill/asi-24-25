import pandas as pd
import os.path
metadata = pd.read_csv('metadata.tsv', sep='\t').set_index('sample-id')

for index, row in metadata.iterrows():
    if not (os.path.exists(row['absolute-filepath'][11:])):
        metadata.drop(index, inplace=True)

metadata.index = range(0, len(metadata))

for index, row in metadata.iterrows():
    if not (os.path.exists(row['absolute-filepath'][11:])):
        print('warning!! i do not exist')

metadata.to_csv('metadata.tsv', sep='\t')

