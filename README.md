# asi-24-25
**Project title: Quantifying diet-based alternate stable states in the gut microbiome through computer modeling**  
Basic outline:   
* Analyze existing data using qiime
* Create models using micom
* Grow in slightly different diets
* Analyze niche space
* Draw conclusions 🕺

## Steps: 
_Note: after steps that involve changing the metadata, you may have to check and manually add the 'sample-id' column title_
1. Fetch data from [gmrepo](https://gmrepo.humangut.info/)
   * Phenotype "healthy," QC status "Good runs," experiment type "Amplicon," at least 18 years old, from one of the countries in the EU
   * See file gmrepo_list.txt
   * Used sra toolkit to fetch data based on the project ids given by gmrepo ([instructions](https://github.com/ncbi/sra-tools/wiki/08.-prefetch-and-fasterq-dump))
   * Generate metadata from the gmrepo_list
   * Note: all of the code for this step is in "reads" (I just haven't uploaded the actual fastq files 😅)
2. Create qiime artifact
   * `qiime tools import --type 'SampleData[SequencesWithQuality]' --input-path reads/metadata.tsv --output-path sequences.qza --input-format SingleEndFastqManifestPhred33V2`
3. Quality filtering
   * Filter, trim, cut out chimeras
   * Returns abundances of each asv (predicted unique sequence)
   * Result: dada directory
   * `qiime dada2 denoise-single --i-demultiplexed-seqs sequences.qza --p-trunc-len 150 --p-n-threads 2 --output-dir dada --verbose`
   * Visualize: `qiime metadata tabulate --m-input-file dada/denoising_stats.qza --o-visualization dada/denoising-stats.qza`
4. Get the new metadata and filter out bad reads
   * Download quality_metadata.tsv from the above visualization
   * Merge with existing metadata
   * Drop all files with percentage non-chimeric < 75
   * Export the new metadata
   * Repeat steps above ^
   * Note: the code used in this step is also in "reads" (the ones with "quality" in their name)
5. Classify into taxonomy
   * Classifier used: SILVA/gtdb
   * `qiime feature-classifier classify-sklearn --i-reads dada/representative_sequences.qza --i-classifier gtdb-classifier.qza --p-n-jobs 2 --o-classification taxa.qza`
   * Visualize: `qiime taxa barplot --i-table dada/table.qza --i-taxonomy taxa.qza --m-metadata-file reads/metadata.tsv --o-visualization taxa_barplot.qza`
6. Use MICOM to create sample-specific metabolic models that contain all taxa in each sample at the correct relative abundance
   * `qiime micom build --i-abundance dada/table.qza --i-taxonomy taxa.qza  --i-models agora_gtdb_genus.qza --p-cutoff 0.0001 --p-threads 4 --o-community-models models.qza --verbose`
   * Write down the models it complains about (for next step)
7. Filter out non-representative models
   * Mostly doing this manually because it's more efficient
   * Copy current models.qza to good-mdoels.qza so we're not destroying data
   * `qiime tools export --input-path good_models.qza --output-path good-models`
   * Manually remove the bad models, and delete them from manifest.csv as well
   * `qiime tools import --type 'CommunityModels[Pickle]' --input-path good-models --output-path good_models.qza`
8. Create diet of interest
   * Download appropriate fluxes from [vmh](https://www.vmh.life/#nutrition)
   * Edit diet-maker.py to have the appropriate file names, and run to create a diet that combines the relevant fluxes
7. Tradeoff analysis
   * Determines best tradeoff between community and individual growth rate
   * `qiime micom tradeoff --i-models good_models.qza --i-medium your_diet.qza --p-threads 4 --o-results tradeoff.qza --verbose`
   * Visualize: `qiime micom plot-tradeoff --i-results tradeoff.qza --o-visualization tradeoff.qza`
   * Look for elbow to determine most appropriate tradeoff
   * Very computationally intensive, so just run with a few diets to get a general idea
8. Grow models in diet!
   * `qiime micom grow --i-models good_models --i-medium your_deiet.qza --p-tradeoff 0.5 --p-threads 4 --o-results growth.qza --verbose`
   * Visualize niche: `qiime micom exchanges-per-taxon --i-results growth.qza --o-visualization niche.qza`
9. Analyze results
    * ...coming soon 😎
