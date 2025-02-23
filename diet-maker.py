import numpy as np
import pandas as pd
from cobra.io import read_sbml_model
from qiime2 import Artifact
from micom.workflows.db_media import check_db_medium, complete_db_medium

# GLOBAL VARIABLES to specify diet !!
add_filepath = 'fluxes/pea-fluxes.tsv'
export_filepath = 'pea-flux-medium'

# ------ DATA SET UP ------
# ... heavily inspired by https://github.com/micom-dev/media/blob/main/recipes/agora.ipynb

annotations = pd.read_csv('agora_metabolites.csv')

control = pd.read_csv('eu-fluxes.tsv', sep='\t', header=0, names=['reaction', 'flux'])
control.loc[control.flux == 0, 'flux'] = 1e-4 # fix truncated values due to vmh bug
control.flux /= 24 # convert from /day to /hour
control.reaction = control.reaction.str[:-3]

add = pd.read_csv(add_filepath, sep='\t', names=['reaction', 'flux'])
add.loc[add.flux == 0, 'flux'] = 1e-4 # fix truncated values due to vmh bug
add.flux /= 24 # convert from /day to /hour
add.reaction = add.reaction.str[:-3]

combined_raw = pd.merge(control, add, how='outer', on=['reaction', 'reaction'], suffixes=('_base', '_added'))
combined_raw.fillna(0, inplace=True)
combined_raw['flux'] = combined_raw['flux_base'] + combined_raw['flux_added']
combined_raw = combined_raw.drop(columns=['flux_base', 'flux_added'])

# need to get it to the same form as https://github.com/micom-dev/media/blob/main/data/agora103_western_gut.csv
combined = pd.DataFrame()
combined['flux'] = combined_raw['flux']
combined['dilution'] = 0.1
combined['reaction'] = combined_raw['reaction'] + '_m'
combined['metabolite'] = combined['reaction'].str[3:]
combined['global_id'] = combined['reaction'].str[:-2] + '(e)'

# ------ IDENTIFYING HUMAN ABSORBTION ------

recon3 = read_sbml_model('Recon3D.xml.gz')
exchanges = pd.Series([r.id for r in recon3.exchanges])
exchanges = exchanges.str.replace('__', '_').str.replace('_e$', '', regex=True)

combined['dilution'] = 1.0
combined.loc[combined.reaction.str[:-2].isin(exchanges), 'dilution'] = 0.1
combined.flux *= combined.dilution

# ------- ADD HOST COMPONENTS --------
# copied from https://github.com/micom-dev/media/blob/main/recipes/vmh_template.ipynb

combined['metabolite'] = combined['metabolite'].str[:-2]
combined.set_index("metabolite", inplace=True)

# mucin
for met in annotations.loc[annotations.metabolite.str.contains("core"), "metabolite"]:
    combined.loc[met, "flux"] = 1

# primary BAs
for met in ["gchola", "tchola"]:
    combined.loc[met, "flux"] = 1

# fiber
combined.loc["cellul", "flux"] = 0.1

# anaerobic
combined.loc["o2", "flux"] = 0.001

combined.reset_index(inplace=True)
combined['metabolite'] = combined.metabolite + '_m'
combined["reaction"] = "EX_" + combined.metabolite
combined['global_id'] = combined['reaction'].str[:-2] + '(e)'
print("COMBINED df after manually adding stuff")
print(combined)
print("10fthf_m row")
print(combined.loc[combined['metabolite'] == '10fthf_m'])

# ------ COMPLETE -------

manifest, imports = complete_db_medium('agora_gtdb_genus.qza', combined, growth=0.001, minimize_components=True)

# this represents the new fluxes
fluxes = imports.max()
fluxes = fluxes[(fluxes > 1e-6) | fluxes.index.isin(combined.reaction)] # relevant fluxes (either nonzero (which means something new was added), or already existed)


print(fluxes)

complete = pd.DataFrame()
complete['reaction'] = fluxes.index
complete['metabolite'] = complete['reaction'].str[3:]
complete['global_id'] = complete['reaction'].str[:-2] + '(e)'
complete['flux'] = fluxes.values
# what I want to do: add (append) all metabolites in combined that don't have anything going on
complete = pd.concat([complete, combined.loc[~combined.metabolite.isin(complete.metabolite)]])

# final verification
#check = check_db_medium('agora_gtdb_genus.qza', complete)
#print(check.can_grow.value_counts())

#export <3
arti = Artifact.import_data('MicomMedium[Global]', complete)
arti.save(export_filepath)
