import unittest
import logging
import os.path as op

from oncotator.MutationData import MutationData
from oncotator.datasources.HgvsChangeTransformingDatasource import HgvsChangeTransformingDatasource
from TestUtils import TestUtils

TestUtils.setupLogging(__file__, __name__)
class HgvsChangeTransformingDatasourceTest(unittest.TestCase):
    _multiprocess_can_split_ = True

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.config = TestUtils.createUnitTestConfig()
        genecode_ds_path = op.join(self.config.get('DEFAULT', 'dbDir'), 'gencode_out2/hg19/gencode.v18.annotation.gtf')
        self.hgvs_datasource = HgvsChangeTransformingDatasource(genecode_ds_path)

    def test_annotate_SNP_missense(self):
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('chr', '13')
        m.createAnnotation('start', 32914782)
        m.createAnnotation('end', 32914782)
        m.createAnnotation('ref_allele', 'C')
        m.createAnnotation('alt_allele', 'T')
        m.createAnnotation('variant_classification', 'Missense_Mutation')
        m.createAnnotation('annotation_transcript', 'ENST00000380152.3')
        m.createAnnotation('genome_change', 'g.chr13:32914782C>T')
        m.createAnnotation('transcript_change', 'c.6290C>T')
        m.createAnnotation('protein_change', 'p.T2097M')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr13.hg19:g.32914782C>T')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000380152.3:c.6290C>T')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), 'ENSP00000369497:p.Thr2097Met')

    def test_annotate_SNP_nonsense(self):
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('chr', '5')
        m.createAnnotation('start', 45303809)
        m.createAnnotation('end', 45303809)
        m.createAnnotation('ref_allele', 'G')
        m.createAnnotation('alt_allele', 'A')
        m.createAnnotation('variant_classification', 'Nonsense_Mutation')
        m.createAnnotation('annotation_transcript', 'ENST00000303230.4')
        m.createAnnotation('genome_change', 'g.chr5:45303809G>A')
        m.createAnnotation('transcript_change', 'c.1510C>T')
        m.createAnnotation('protein_change', 'p.R504*')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr5.hg19:g.45303809G>A')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000303230.4:c.1510C>T')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), 'ENSP00000307342:p.Arg504*')

    def test_annotate_renders_with_no_build(self):
        """If mutation instance being annotated does not have a build value or is '', annotate should
        return a genome_change value with just chr. i.e. chr2:g.80529551A>C vs. chr2.hg19:g.80529551A>C"""
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('chr', '2')
        m.createAnnotation('start', 80529551)
        m.createAnnotation('end', 80529551)
        m.createAnnotation('ref_allele', 'A')
        m.createAnnotation('alt_allele', 'C')
        m.createAnnotation('variant_classification', 'Intron')
        m.createAnnotation('annotation_transcript', 'ENST00000402739.4')
        m.createAnnotation('transcript_strand', '+')
        m.createAnnotation('genome_change', 'g.chr2:80529551A>C')
        m.createAnnotation('transcript_change', '')
        m.createAnnotation('protein_change', '')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr2:g.80529551A>C')

    def test_annotate_SNP_intron(self):
        #+ strand transcript
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('chr', '2')
        m.createAnnotation('start', 80529551)
        m.createAnnotation('end', 80529551)
        m.createAnnotation('ref_allele', 'A')
        m.createAnnotation('alt_allele', 'C')
        m.createAnnotation('variant_classification', 'Intron')
        m.createAnnotation('annotation_transcript', 'ENST00000402739.4')
        m.createAnnotation('transcript_strand', '+')
        m.createAnnotation('genome_change', 'g.chr2:80529551A>C')
        m.createAnnotation('transcript_change', '')
        m.createAnnotation('protein_change', '')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr2.hg19:g.80529551A>C')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000402739.4:c.1057-90785A>C')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), '')

        #- strand transcript
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('chr', '10')
        m.createAnnotation('start', 118891993)
        m.createAnnotation('end', 118891993)
        m.createAnnotation('ref_allele', 'A')
        m.createAnnotation('alt_allele', 'G')
        m.createAnnotation('variant_classification', 'Intron')
        m.createAnnotation('annotation_transcript', 'ENST00000277905.2')
        m.createAnnotation('transcript_strand', '-')
        m.createAnnotation('genome_change', 'g.chr10:118891993A>G')
        m.createAnnotation('transcript_change', '')
        m.createAnnotation('protein_change', '')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr10.hg19:g.118891993A>G')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000277905.2:c.430-5T>C')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), '')

    def test_annotate_SNP_5_utr(self):
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('chr', '7')
        m.createAnnotation('start', 6865862)
        m.createAnnotation('end', 6865862)
        m.createAnnotation('ref_allele', 'G')
        m.createAnnotation('alt_allele', 'C')
        m.createAnnotation('variant_classification', "5'UTR")
        m.createAnnotation('annotation_transcript', 'ENST00000316731.8')
        m.createAnnotation('transcript_strand', '-')
        m.createAnnotation('genome_change', 'g.chr7:6865862G>C')
        m.createAnnotation('transcript_change', '')
        m.createAnnotation('protein_change', '')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr7.hg19:g.6865862G>C')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000316731.8:c.-34C>G')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), '')

    def test_annotate_SNP_3_utr(self):
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('chr', '8')
        m.createAnnotation('start', 27145409)
        m.createAnnotation('end', 27145409)
        m.createAnnotation('ref_allele', 'G')
        m.createAnnotation('alt_allele', 'A')
        m.createAnnotation('variant_classification', "3'UTR")
        m.createAnnotation('annotation_transcript', 'ENST00000521253.1')
        m.createAnnotation('transcript_strand', '-')
        m.createAnnotation('genome_change', 'g.chr8:27145409G>A')
        m.createAnnotation('transcript_change', '')
        m.createAnnotation('protein_change', '')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr8.hg19:g.27145409G>A')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000521253.1:c.*220C>T')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), '')

    def test_annotate_SNP_igr(self):
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('variant_classification', 'IGR')
        m.createAnnotation('chr', '15')
        m.createAnnotation('start', 30938316)
        m.createAnnotation('end', 30938316)
        m.createAnnotation('ref_allele', 'G')
        m.createAnnotation('alt_allele', 'A')
        m.createAnnotation('genome_change', '')
        m.createAnnotation('transcript_change', '')
        m.createAnnotation('protein_change', '')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr15.hg19:g.30938316G>A')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), '')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), '')

    def test_annotate_SNP_silent(self):
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('variant_classification', 'Silent')
        m.createAnnotation('chr', '1')
        m.createAnnotation('start', 19549914)
        m.createAnnotation('end', 19549914)
        m.createAnnotation('ref_allele', 'G')
        m.createAnnotation('alt_allele', 'A')
        m.createAnnotation('annotation_transcript', 'ENST00000477853.1')
        m.createAnnotation('genome_change', 'g.chr1:19549914G>A')
        m.createAnnotation('transcript_change', 'c.2352C>T')
        m.createAnnotation('protein_change', 'p.I784I')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr1.hg19:g.19549914G>A')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000477853.1:c.2352C>T')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), '')

    def test_annotate_SNP_nonstop(self):
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('variant_classification', 'Nonstop_Mutation')
        m.createAnnotation('chr', '7')
        m.createAnnotation('start', 55273310)
        m.createAnnotation('end', 55273310)
        m.createAnnotation('ref_allele', 'A')
        m.createAnnotation('alt_allele', 'G')
        m.createAnnotation('annotation_transcript', 'ENST00000275493.2')
        m.createAnnotation('genome_change', 'g.chr7:55273310A>G')
        m.createAnnotation('transcript_change', 'c.3633A>G')
        m.createAnnotation('protein_change', 'p.*1211W')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr7.hg19:g.55273310A>G')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000275493.2:c.3633A>G')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), 'ENSP00000275493:p.*1211Trpext*6') #6 new amino acids added until another stop codon is encountered
        # "p.*1211Trpext?" would describe a variant in the stop codon at position 1211 changing it to a codon for Tryptophan (Trp, W) and adding a tail of new amino acids of unknown length since the shifted frame does not contain a new stop codon.

    def test_annotate_SNP_splice_site(self):
        #splice site mutation occuring in intron prior coding start position
        #rs61191258
        m = MutationData()
        m.createAnnotation('variant_type', 'SNP')
        m.createAnnotation('build', 'hg19')
        m.createAnnotation('variant_classification', 'Splice_Site')
        m.createAnnotation('chr', '19')
        m.createAnnotation('start', 52994576)
        m.createAnnotation('end', 52994576)
        m.createAnnotation('ref_allele', 'G')
        m.createAnnotation('alt_allele', 'A')
        m.createAnnotation('annotation_transcript', 'ENST00000421239.2')
        m.createAnnotation('transcript_strand', '+')
        m.createAnnotation('genome_change', 'g.chr19:52994576G>A')
        m.createAnnotation('transcript_change', '')
        m.createAnnotation('protein_change', '')
        m = self.hgvs_datasource.annotate_mutation(m)

        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr19.hg19:g.52994576G>A')
        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000421239.2:c.-121-1G>A')
        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), '')

        #splice site mutation occuring in intron after coding start position
        # TODO
#
#    def test_annotate_SNP_de_novo_start(self):
#        m = MutationData()
#        m.createAnnotation('variant_type', 'SNP')
#        m.createAnnotation('variant_classification', 'De_novo_Start_OutOfFrame')
#        m.createAnnotation('annotation_transcript', 'ENST00000372237.3')
#        m.createAnnotation('genome_change', 'g.chr1:45140082G>T')
#        m.createAnnotation('transcript_change', '')
#        m.createAnnotation('protein_change', '')
#        m = self.hgvs_datasource.annotate_mutation(m)
#
#        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr1.hg19:g.45140082G>T')
#        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000372237.3:c.-121-1G>C')
#        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), '')
#
#    def test_annotate_ONP_missense(self):
#        m = MutationData()
#        m.createAnnotation('variant_type', 'DNP')
#        m.createAnnotation('variant_classification', 'Missense_Mutation')
#        m.createAnnotation('annotation_transcript', 'ENST00000215939.2')
#        m.createAnnotation('genome_change', 'g.chr22:27003913_27003914CC>AT')
#        m.createAnnotation('transcript_change', 'c.371_372GG>AT')
#        m.createAnnotation('protein_change', 'p.W124Y')
#        m = self.hgvs_datasource.annotate_mutation(m)
#
#        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr22.hg19:g.27003913_27003914CC>AT')
#        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000215939.2:c.371_372GG>AT')
#        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), 'ENSP00000215939:p.Trp124Tyr')
#
#    def test_annotate_INS_inframe(self):
#        m = MutationData()
#        m.createAnnotation('variant_type', 'INS')
#        m.createAnnotation('variant_classification', 'In_Frame_Ins')
#        m.createAnnotation('annotation_transcript', 'ENST00000512097.3')
#        m.createAnnotation('genome_change', 'g.chr5:113698631_113698632insGCC')
#        m.createAnnotation('transcript_change', 'c.159_160insGCC')
#        m.createAnnotation('protein_change', 'p.54_54A>AA')
#        m = self.hgvs_datasource.annotate_mutation(m)
#
#        #this ins of GCC occurs in a GCC-repeat region and thus need to 3' adjust position for HGVS compliance
#        # it is technically a duplication
#        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr5.hg19:g.113698641_113698643dupGCC')
#        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000512097.3:c.169_171dupGCC')
#        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), 'ENSP00000215939:p.Ala58dup')
#
#    def test_annotate_INS_frameshift(self):
#        m = MutationData()
#        m.createAnnotation('variant_type', 'INS')
#        m.createAnnotation('variant_classification', 'Frame_Shift_Ins')
#        m.createAnnotation('annotation_transcript', 'ENST00000324803.4')
#        m.createAnnotation('genome_change', 'g.chr4:1388441_1388442insCG')
#        m.createAnnotation('transcript_change', 'c.142_143insCG')
#        m.createAnnotation('protein_change', 'p.M48fs')
#        m = self.hgvs_datasource.annotate_mutation(m)
#
#        #this ins of CG does NOT occurs next to a CG and does not need to be position adjusted
#        # it is technically an insertion
#        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr4.hg19:1388441_1388442insCG')
#        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000324803.4:c.142_143insCG')
#        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), 'ENSP00000323978:p.Met48fs')
#
#    def test_annotate_DEL_inframe(self):
#        m = MutationData()
#        m.createAnnotation('variant_type', 'DEL')
#        m.createAnnotation('variant_classification', 'In_Frame_Del')
#        m.createAnnotation('annotation_transcript', 'ENST00000603540.1')
#        m.createAnnotation('genome_change', 'g.chr14:70924869_70924871delATG')
#        m.createAnnotation('transcript_change', 'c.653_655delATG')
#        m.createAnnotation('protein_change', 'p.D219del')
#        m = self.hgvs_datasource.annotate_mutation(m)
#
#        #this deletion is straightforward, no position adjustments necessary
#        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr14.hg19:70924869_70924871delATG')
#        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000603540.1:c.653_655delATG')
#        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), 'ENSP00000474385:p.Asp219del')
#
#    def test_annotate_DEL_frameshift(self):
#        m = MutationData()
#        m.createAnnotation('variant_type', 'DEL')
#        m.createAnnotation('variant_classification', 'Frame_Shift_Del')
#        m.createAnnotation('annotation_transcript', 'ENST00000294618.7')
#        m.createAnnotation('genome_change', 'g.chr19:11348960delG')
#        m.createAnnotation('transcript_change', 'c.1664delC')
#        m.createAnnotation('protein_change', 'p.P555fs')
#        m = self.hgvs_datasource.annotate_mutation(m)
#
#        #Here only the genomic change needs to get '3 shifted because the transcript is negative strand 
#        #and the coding postion is already the most 3'
#        self.assertEqual(m.annotations['HGVS_genomic_change'].getValue(), 'chr19.hg19:11348962delG')
#        self.assertEqual(m.annotations['HGVS_coding_DNA_change'].getValue(), 'ENST00000294618.7:c.1664delC')
#        self.assertEqual(m.annotations['HGVS_protein_change'].getValue(), 'ENSP00000294618:p.P555fs')



