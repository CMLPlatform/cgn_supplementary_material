# cgn_supplementary_material

## exio_mr_hiot_v3.3.15_2011.
It includes extention accounts from EXIOBASE v.3.3.15 coverted tab-delimited files:
* Resource extraction per economic activity (RE_ACT)
* Resource extraction per final demand category (RE_FD)
* Waste supply per economic activity (WS_ACT)
* Waste supply per final demand category (WS_FD)
* Stock additions per economic activity (SA_ACT)
* Stock additions per final demand category (SA_FD)
* Waste use per economic activity (WU_ACT)
* Stock depletion per final demand category (SD)
* Emissions per economic activity (EM_ACT)
* Emissions per final demand category (EM_FD)
* Population per country (POP)

## code.py
Phyton script returns an excel file with:
* Results of global circularity gap per material category (data_glo)
* Results of circularity gap per country (data_cou)
* Results of circularity gap per aggregated region (data_reg) 

## sankey.py
Phyton script returns Sankey diagram using floweaver software

**Note: SankeyWidget performs on Jupyter Notebook** 

## results.xls 
> Excel file with results from 'code.py'

## analysis.xls
It includes the circularity gap analysis and figures based on 'results.xlsb' source data  

## exio_class.xls
It includes material group classificafication used in Sankey diagram from EXIOBASE v.3.3.15 categories  

## wb_to_exio_cov.xls
Excel file coverts datasets from World Bank Statistics  

## procedure.docx
Word file contains:
* Procedure to import EXIOBASE v3.3.15, use of 'code.py', 'sankey.py', 'results.xls' and 'analysis.xls' 
* A comparison between data from EXIOBASE v3.3.15 and other sources of material flow accounts   
