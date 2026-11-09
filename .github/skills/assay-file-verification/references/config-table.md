# Assay Configuration Table

Extracted from `isatools/resources/config/xml/*.xml`. A STUDY ASSAYS row selects
its table config by lowercased
`(Study Assay Measurement Type, Study Assay Technology Type)`.
`isatab_configurator.load()` builds this mapping; rule 4002 errors when the pair
has no entry.

| Config file | Study Assay Measurement Type | Study Assay Technology Type |
|-------------|------------------------------|-----------------------------|
| cellcount_flowcytometry.xml | cell counting | flow cytometry |
| cellsorting_flowcyt.xml | cell sorting | flow cytometry |
| clinical_chemistry.xml | clinical chemistry analysis | (empty) |
| copynumvariation_micro.xml | copy number variation profiling | DNA microarray |
| copynumvariation_seq.xml | copy number variation profiling | nucleotide sequencing |
| dnamethylation_micro.xml | DNA methylation profiling | DNA microarray |
| dnamethylation_seq.xml | DNA methylation profiling | nucleotide sequencing |
| envgen_survey_seq.xml | environmental gene survey | nucleotide sequencing |
| genome_seq.xml | genome sequencing | nucleotide sequencing |
| hematology.xml | hematology | (empty) |
| heterozygosity_micro.xml | loss of heterozygosity profiling | DNA microarray |
| histology.xml | histology | (empty) |
| histonemodification_seq.xml | histone modification profiling | nucleotide sequencing |
| isotopologue_ms.xml | isotopologue distribution analysis | mass spectrometry |
| isotopomer_nmr.xml | isotopomer analysis | NMR spectroscopy |
| metaboliteprofiling_ms.xml | metabolite profiling | mass spectrometry |
| metaboliteprofiling_nmr.xml | metabolite profiling | NMR spectroscopy |
| metagenome_seq.xml | metagenome sequencing | nucleotide sequencing |
| phenotyping_imaging.xml | phenotyping analysis | imaging |
| ppi_detection_micro.xml | protein-protein interaction detection | protein microarray |
| protein_dna_binding_ident_micro.xml | protein-DNA binding site identification | DNA microarray |
| protein_dna_binding_ident_seq.xml | protein-DNA binding site identification | nucleotide sequencing |
| protein_expression_ge.xml | protein expression profiling | gel electrophoresis |
| protein_expression_micro.xml | protein expression profiling | protein microarray |
| protein_expression_ms.xml | protein expression profiling | mass spectrometry |
| proteinident_ms.xml | protein identification | mass spectrometry |
| snpanalysis_micro.xml | SNP analysis | DNA microarray |
| tfbsident_micro.xml | transcription factor binding site identification | DNA microarray |
| tfbsident_seq.xml | transcription factor binding site identification | nucleotide sequencing |
| transcription_micro.xml | transcription profiling | DNA microarray |
| transcription_rtpcr.xml | transcription profiling | real time PCR |
| transcription_seq.xml | transcription profiling | nucleotide sequencing |
| untargetedmetaboliteprofiling_nmr.xml | untargeted metabolite profiling | NMR spectroscopy |

Notes:
- Matching is case-insensitive (the key is lowercased both sides), but the
  labels must otherwise be an exact match — including the empty technology type
  for `clinical_chemistry`, `hematology`, `histology`.
- `investigation.xml` and `studySample.xml` (`("[investigation]", "")`,
  `("[sample]", "")`) are not assay configs; they drive investigation- and
  study-table validation.
- Ontology-annotate the types with the term labels above (and OBI accessions,
  e.g. `http://purl.obolibrary.org/obo/OBI_0000424` for transcription profiling,
  `OBI_0000626` for nucleotide sequencing) and declare the source in
  ONTOLOGY SOURCE REFERENCE (rule 3008).
