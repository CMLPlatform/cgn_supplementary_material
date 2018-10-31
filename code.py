# -*- coding: utf-8 -*-
"""
This code retrieves the calculation of circularity gap per country
in an Excel file

The Excel file contains three spreadsheet, as:
    1) cg_world = global input-output flows
      (also used for creating Sankey diagram)
    2) cg_per_country = results of material flows per country
    3) cg_per_region = results of material flows per aggregated region

Database: EXIOBASE MR-HIOT v.3.3.15.

Software version: Phyton 3.6.

Created on Thu Sep 20 11:53:34 2018

Updated on Sat Oct 27 17:40:00 2018

@author: aguilarga
"""

import pandas as pd
import numpy as np
from pandas import read_csv
from pandas import ExcelWriter
from datetime import datetime


def main():
    # CALCULATING CIRCULARITY GAP
    path = 'exio_mr_hiot_v3.3.15_2011'
    RE = read_csv(path + '\RE_ACT.txt', sep='\t', index_col=[0, 1],
                  header=[0, 1], decimal=',')  # resource extraction matrix
    RE_FD = read_csv(path + '\RE_FD.txt', sep='\t', index_col=[0, 1],
                     header=[0, 1], decimal=',')  # resource ext FD matrix
    WS = read_csv(path + '\WS_ACT.txt', sep='\t', index_col=[0, 1],
                  header=[0, 1], decimal=',')  # waste supply matrix
    WS_FD = read_csv(path + '\WS_FD.txt', sep='\t', index_col=[0, 1],
                     header=[0, 1], decimal=',')  # waste from FD matrix
    WU = read_csv(path + '\WU_ACT.txt', sep='\t', index_col=[0, 1],
                  header=[0, 1], decimal=',')  # waste use matrix
    SA = read_csv(path + '\SA_ACT.txt', sep='\t', index_col=[0, 1],
                  header=[0, 1], decimal=',')  # stock additions matrix
    SA_FD = read_csv(path + '\SA_FD.txt', sep='\t', index_col=[0, 1],
                     header=[0, 1], decimal=',')  # add_stocks from FD
    SD = read_csv(path + '\SD.txt', sep='\t', index_col=[0, 1],
                  header=[0, 1], decimal=',')    # stock depletion matrix
    EM = read_csv(path + '\EM_ACT.txt', sep='\t', index_col=[0, 1, 2],
                  header=[0, 1], decimal=',')  # emissions matrix
    EM_FD = read_csv(path + '\EM_FD.txt', sep='\t', index_col=[0, 1, 2],
                     header=[0, 1], decimal=',')  # emissions from FD matrix
    pop = read_csv(path + '\POP.txt', sep='\t', index_col=[0],
                   decimal=',')  # population vector
    # CIRCULARITY GAP GLOBAL
    cg_world = cal_cg_world(RE, RE_FD, WS, WS_FD, WU, SA, SA_FD, SD,
                            EM, EM_FD)
    # CIRCULARITY GAP PER COUNTRY/REGION
    country_lab = WS_FD.columns.levels[0][WS_FD.columns.labels[0][0::6]]
    val_lab = ['Resource extraction (t)', 'Waste generation (t)',
               'Stock depletion (t)',
               'Waste recovery (t)', 'Circularity gap (Gt)',
               'Stock additions (t)',
               'Dissipative emissions (t)', 'Population (pc)']
    emp = []
    for i in country_lab:
        df = cal_cg_country(i, RE, RE_FD, WS, WS_FD, WU, SA, SA_FD, SD,
                            EM, EM_FD, pop)
        emp.append(df)
    cg_per_country = pd.DataFrame(emp, index=country_lab, columns=val_lab)
    cg_per_region = region_agg(cg_per_country)
    return cg_world, cg_per_country, cg_per_region


# FUNCTIONS


def cal_cg_world(RE, RE_FD, WS, WS_FD, WU, SA, SA_FD, SD, EM, EM_FD):
    # INDEX
    rf_ind = np.arange(24, 33)  # fossil fuels extraction
    rb_ind = [0, 3, 8, 12, 14, 33]  # biomass extraction
    rm_ind = [1, 5, 6, 9, 10, 13, 16, 17, 19, 21, 22, 23]  # metals extraction
    rn_ind = [2, 4, 7, 11, 15, 18, 20, 34]  # nonmetallic minerals extraction
    ef_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
              22, 23, 24, 25, 26, 27, 28, 29, 30,
              31, 32, 33, 34, 35, 36, 37, 38, 39,
              40, 41, 42, 43, 44, 45, 46, 47, 48,
              49, 63, 65]  # fossil fuels emissions
    eb_ind = [52, 64]  # biomass emissions
    em_ind = [13, 14, 15, 16, 17, 18, 19, 20, 21, 55, 56,
              57, 58, 59, 60, 61]  # metals emissions
    en_ind = [50, 51, 53, 54, 62]  # nonmetallic minerals emissions
    wf_ind = [5, 7, 15]  # fossil fuels waste/stock flows
    wb_ind = [0, 1, 2, 3, 4, 16]  # biomass waste/stock flows
    wm_ind = np.arange(8, 14)  # metals waste/stock flows
    wn_ind = [6, 14]  # nonmetallic minerals waste/stock flows
    wr_ind = [15, 16, 50, 52, 59, 65, 69, 72, 74, 76,
              78, 80, 82, 93, 94, 101, 114, 146, 147,
              148, 149, 150]  # recovery activites index
    co2 = 44  # molar mass carbon dioxide
    co = 28  # molar mass carbon monoxide
    c = 12  # molar mass carbon
    # RESOURCE EXTRACTION CALCULATION
    ref = RE.iloc[rf_ind, :].sum().sum()  # fossil fuels extraction
    reb_ty = RE.iloc[rb_ind, :].sum(1)  # all biomass resource in CO2
    reb_ty[5] = reb_ty[5]*c/co2  # covert CO2 mass in C mass
    reb = reb_ty.sum()  # biomass extraction
    rem = RE.iloc[rm_ind, :].sum().sum()  # metals extraction
    ren = (RE.iloc[rn_ind, :].sum().sum() +
           RE_FD.iloc[rn_ind, :].sum().sum())  # nonmet minerals extraction
    # WASTE SUPPLY CALCULATION
    wsf = (WS.iloc[wf_ind, :].sum().sum() +
           WS_FD.iloc[wf_ind, :].sum().sum())  # sum of fossil fuels waste
    wsb = (WS.iloc[wb_ind, :].sum().sum() +
           WS_FD.iloc[wb_ind, :].sum().sum())  # sum of biomass waste
    wsm = (WS.iloc[wm_ind, :].sum().sum() +
           WS_FD.iloc[wm_ind, :].sum().sum())  # sum of metals waste
    wsn = (WS.iloc[wn_ind, :].sum().sum() +
           WS_FD.iloc[wn_ind, :].sum().sum())  # sum of nonmetallic waste
    # WASTE RECOVERY CALCULATION
    emp = []  # empty array
    for i in wr_ind:
        act_rec = WU.iloc[:, i::164].sum(1)
        emp.append(act_rec)
        WR = pd.DataFrame(emp).T  # waste recovery matrix
    wrf = WR.iloc[wf_ind, :].sum().sum()  # sum of fossil fuels recovered
    wrb = WR.iloc[wb_ind, :].sum().sum()  # sum of biomass recovered
    wrm = WR.iloc[wm_ind, :].sum().sum()  # sum of metals recovered
    wrn = WR.iloc[wn_ind, :].sum().sum()  # sum of nonmetallic recovered
    # STOCK ADDITIONS CALCULATION
    saf = (SA.iloc[wf_ind, :].sum().sum() +
           SA_FD.iloc[wf_ind, :].sum().sum())  # sum of fossil stock added
    sab = (SA.iloc[wb_ind, :].sum().sum() +
           SA_FD.iloc[wb_ind, :].sum().sum())  # sum of biomass stock added
    sam = (SA.iloc[wm_ind, :].sum().sum() +
           SA_FD.iloc[wm_ind, :].sum().sum())  # sum of metals stock added
    san = (SA.iloc[wn_ind, :].sum().sum() +
           SA_FD.iloc[wn_ind, :].sum().sum())  # sum of nonmetallic stock added
    # STOCK DEPLETION CALCULATION
    sdf = SD.iloc[wf_ind, :].sum().sum()  # sum of fossil fuels stock depleted
    sdb = SD.iloc[wb_ind, :].sum().sum()  # sum of biomass stock depleted
    sdm = SD.iloc[wm_ind, :].sum().sum()  # sum of metals stock depleted
    sdn = SD.iloc[wn_ind, :].sum().sum()  # sum of nonmetallic stock depleted
    # DISSIPATIVE EMISSIONS
    emf_ty = (EM.iloc[ef_ind, :].sum(1) +
              EM_FD.iloc[ef_ind, :].sum(1))  # sum of all fossil emissions
    emf_ty[0] = emf_ty[0]*c/co2  # convert CO2 mass in C mass
    emf_ty[10] = emf_ty[10]*c/co  # covert CO mass in C mass
    emf = emf_ty.sum()  # fossil fuels emissions (in equivalent of C mass)
    emb_ty = (EM.iloc[eb_ind, :].sum(1) +
              EM_FD.iloc[eb_ind, :].sum(1))  # biomass emissions per type
    emb_ty[1] = emb_ty[1]*c/co2  # convert CO2 mass in C mass
    emb = emb_ty.sum()  # biomass emissions (in equivalent of C mass)
    emm = (EM.iloc[em_ind, :].sum().sum() +
           EM_FD.iloc[em_ind, :].sum().sum())  # metal emissions
    emn = (EM.iloc[en_ind, :].sum().sum() +
           EM_FD.iloc[en_ind, :].sum().sum())  # nonmet mineral emissions
    # MATERIAL DISPERSED AND UNREGISTERED WASTE
    mdf = (ref + wrf) - (wsf + saf + emf)  # fossil fuels dispersed
    mdb = (reb + wrb) - (wsb + sab + emb)  # biomass dispersed
    mdm = (rem + wrm) - (wsm + sam + emm)  # metal dispersed
    mdn = (ren + wrn) - (wsn + san + emn)  # nonmetal minerals dispersed
    # DOMESTIC PROCESSED OUTPUT
    dpf = emf + mdf  # fossil fuels processed output
    dpb = emb + mdb  # biomass processed output
    dpm = emm + mdm  # metal processed output
    dpn = emn + mdn  # nonmetal minerals processed output
    # CIRCULARITY GAP CALCULATION
    cgf = wsf + sdf - wrf  # circularity gap fossil fuels
    cgb = wsb + sdb - wrb  # circularity gap biomass
    cgm = wsm + sdm - wrm  # circularity gap metals
    cgn = wsn + sdn - wrn  # circularity gap nonmetals
    # RESULTS
    results = pd.DataFrame([ref, reb, rem, ren,
                            dpf, dpb, dpm, dpn,
                            wsf, wsb, wsm, wsn,
                            saf, sab, sam, san,
                            sdf, sdb, sdm, sdn,
                            cgf, cgb, cgm, cgn,
                            wrf, wrb, wrm, wrn])
    results = results/1E09
    results.index = ['re_fossil', 're_biomass', 're_metal',
                     're_non-metal', 'dpo_fossil', 'dpo_biomass',
                     'dpo_metal', 'dpo_non-metal', 'w_fossil',
                     'w_biomass', 'w_metal', 'w_non-metal',
                     's_add_fossil', 's_add_biomass', 's_add_metal',
                     's_add_non-metal', 's_dep_fossil',
                     's_dep_biomass', 's_dep_metal',
                     's_dep_non-metal', 'gap_fossil', 'gap_biomass',
                     'gap_metal', 'gap_non-metal', 'w_rec_fossil',
                     'w_rec_biomass', 'w_rec_metal',
                     'w_rec_non-metal']
    results.columns = ['Gigatonnes (Gt)']
    return results


def cal_cg_country(c_name, RE, RE_FD, WS, WS_FD, WU, SA, SA_FD, SD, EM, EM_FD,
                   pop):
    # INDEX
    r_ind = np.arange(0, 35)  # resource categories index
    w_ind = np.arange(0, 17)  # waste categories index
    wr_ind = [15, 16, 50, 52, 59, 65, 69, 72, 74, 76,
              78, 80, 82, 93, 94, 101, 114, 146, 147,
              148, 149, 150]  # recovery activites index
    co2 = 44  # molar mass carbon dioxide
    c = 12  # molar mass carbon
    # SETTIINGS
    RE = RE.iloc[r_ind, :]  # resource excluding oxigen and water
    RE_FD = RE_FD.iloc[r_ind, :]  # resource excluding oxigen and water
    WS = WS.iloc[w_ind, :]  # waste supply for selected waste class
    WS_FD = WS_FD.iloc[w_ind, :]  # waste supply  FD for selected waste class
    WU = WU.iloc[w_ind, :]  # waste use for selected waste class
    SA = SA.iloc[w_ind, :]  # stock additions for selected waste class
    SA_FD = SA_FD.iloc[w_ind, :]  # stock additions FD for selected waste class
    SD = SD.iloc[w_ind, :]  # stock depletion for selected waste class
    # RESOURCE EXTRACTION CALCULATION
    re_ty = RE.loc[:, c_name].sum(1)  # all extracted resource types
    re_ty[33] = re_ty[33]*c/co2  # covert CO2 mass in C mass
    re = (re_ty.sum() + RE_FD.loc[:, c_name].sum().sum())
    # WASTE GENERATION CALCULATION
    ws = (WS.loc[:, c_name].sum().sum() +
          WS_FD.loc[:, c_name].sum().sum())
    # WASTE RECOVERY CALCULATION
    wuc = WU.loc[:, c_name]  # waste use per country
    wr = wuc.iloc[:, wr_ind].sum().sum()  # waste recovery per country
    # ADDITIONS TO STOCK CALCULATION
    sa = (SA.loc[:, c_name].sum().sum() +
          SA_FD.loc[:, c_name].sum().sum())
    # STOCK DEGRADATION CALCULATION
    sd = SD.loc[:, c_name].sum().sum()
    # EMISSIONS CALCULATION
    em = (EM.loc[:, c_name].sum().sum() +
          EM_FD.loc[:, c_name].sum().sum())
    # CIRCULARITY GAP CALCULATION
    cg = ws + sd - wr
    # POPULATION CALCULATION
    pp = pop.loc[c_name].sum()
    # RESULTS
    results = [re, ws, sd, wr, cg, sa, em, pp]
    return results


def region_agg(df):
    world = pd.DataFrame(df.sum(0), columns=['World'])
    eu_index = ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI',
                'FR', 'GR', 'HU', 'HR', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT',
                'NL', ' PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB', 'NO', 'CH',
                'WE']
    europe = pd.DataFrame(df.loc[eu_index, :].sum(0), columns=['Europe'])
    na_index = ['US', 'CA']
    na = pd.DataFrame(df.loc[na_index, :].sum(0), columns=['North America'])
    cn = pd.DataFrame(df.loc['CN', :])
    cn.columns = ['China']
    ru = pd.DataFrame(df.loc['RU', :])
    ru.columns = ['Russia']
    india = pd.DataFrame(df.loc['IN', :])
    india.columns = ['India']
    au = pd.DataFrame(df.loc['AU', :])
    au.columns = ['Australia']
    jp = pd.DataFrame(df.loc['JP', :])
    jp.columns = ['Japan']
    af_index = ['ZA', 'WF']
    af = pd.DataFrame(df.loc[af_index, :].sum(0), columns=['Africa'])
    me_index = ['TR', 'WM']
    me = pd.DataFrame(df.loc[me_index, :].sum(0), columns=['Middle East'])
    lam_index = ['BR', 'MX', 'WL']
    lam = pd.DataFrame(df.loc[lam_index, :].sum(0), columns=['Latin America'])
    ap_index = ['KR', 'ID', 'WA']
    ap = pd.DataFrame(df.loc[ap_index, :].sum(0), columns=['Asia and Pacific'])
    df_agg = pd.concat([world, europe, na, cn, ru, india, au, jp, lam, me, af,
                        ap], axis=1)
    return df_agg.T


cg_world, cg_per_country, cg_per_region = main()
# SAVE RESULTS
writer = ExcelWriter("results_" +
                     datetime.now().strftime('%Y%m%d') + ".xlsx")
cg_world.to_excel(writer, 'data_glo')
cg_per_country.to_excel(writer, 'data_cou')
cg_per_region.to_excel(writer, 'data_reg')
writer.save()
