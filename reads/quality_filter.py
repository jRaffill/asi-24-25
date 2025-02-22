import pandas as pd
metadata = pd.read_csv('prefilter_metadata.tsv', sep='\t').set_index('sample-id')
qualities = pd.read_csv('quality_metadata.tsv', sep='\t', usecols=['sample-id', 'percentage of input non-chimeric']).set_index('sample-id')

metadata = qualities.join(metadata)
indexes = metadata[ metadata['percentage of input non-chimeric'] < 75 ].index
metadata = metadata.drop(indexes)
metadata = metadata.drop(columns=['percentage of input non-chimeric'])
metadata.index = range(0, len(metadata))
print(metadata)
metadata.to_csv('metadata.tsv', sep='\t')

