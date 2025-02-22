import pandas as pd
import copy

metadata = pd.read_csv('source_metadata.tsv', sep='\t')
ids = metadata['Run ID'].iloc[1:]
ids.to_csv('ids.csv', index=False, header=False)
metadata = metadata.drop(columns=['Project ID', 'Experiment type', 'Nr. reads sequenced', 'Disease MESH ID', 'Disease name', 'QC status', 'Nr. associated phenotypes', 'Recent antibiotics use'])

metadata.set_index('Run ID', inplace=True)

def copy_rows(row):
    global metadata
    metadata.drop(metadata[metadata['Run ID'] == row['Run ID']].index, inplace=True)
    copied = copy.copy(row)
    row['Run ID'] += '_1'
    copied['Run ID'] += '_2'
    metadata = pd.concat([metadata, pd.DataFrame(row).T], ignore_index=True)
    metadata = pd.concat([metadata, pd.DataFrame(copied).T], ignore_index=True)
    return

need_to_copy = metadata.filter(like='SRR', axis=0)
need_to_copy.reset_index(inplace=True)
metadata.reset_index(inplace=True)
need_to_copy.apply(copy_rows, axis=1)

metadata.rename(columns={'Run ID': 'absolute-filepath'}, inplace=True)
metadata['absolute-filepath'] = '$PWD/reads/' + metadata['absolute-filepath'] + '.fastq'

metadata['sample-id'] = range(0, len(metadata))
metadata = metadata[['sample-id', 'absolute-filepath', 'Country', 'Sex', 'Host age', 'BMI']]
metadata.set_index('sample-id', inplace=True)
print(metadata)
#metadata.to_csv('metadata.tsv', sep='\t')

