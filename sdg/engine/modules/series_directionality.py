'Desired direction by actual API series, reviewed on 2026-11-02 using the UNSD Technical Note for Progress Assessment 2026 and measure definitions. Explicitly document interpretive exceptions. Original observations are preserved.'
NEGATIVE = set('AG_FPA_HMFP DT_TDS_DECT EG_EGY_PRIM EN_ATM_CO2MVA EN_ATM_PM25 EN_LND_SLUM EN_MAT_DOMCMPG EN_MAT_DOMCMPT ER_FFS_CMPT_GDP ER_FFS_CMPT_PC_CD ER_H2O_STRESS ER_UNK_LBREDN IC_FRM_BRIB SH_ALC_CONSPT SH_DTH_NCOM SH_DYN_MORT SH_HIV_INCD SH_OOP_XPD_EARNNET40 SH_PRV_SMOK SH_SAN_DEFECT SH_STA_MALR SH_STA_MORT SH_STA_POISN SH_STA_STNT SH_STA_TRAF SH_STA_WASHARI SH_STA_WAST SH_TBS_INCD SI_POV_DAY1 SI_RMT_COST SL_ISV_IFEM SL_TLF_NEET SL_TLF_UEM SN_ITK_DEFC SP_DYN_ADKL SP_DYN_MRBF15 VC_IHR_PSRC VC_PRS_UNSNT VC_VAW_MARR'.split())
POSITIVE = set('AG_LND_FRST AG_LND_FRSTBIOPHA AG_LND_SUST_PRXCSS AG_PRD_ORTIND BX_TRF_PWKR DC_FTA_TOTAL DC_ODA_BDVL DC_TOF_AGRL DC_TOF_INFRAL DC_TOF_SCHIPSL DC_TOF_TRDDBML DC_TOF_WASHL DC_TRF_TFDV EG_ACS_ELEC EG_EGY_CLEAN EG_FEC_RNEW EN_EWT_RCYV EN_LKRV_PWAP EN_WWT_WWDS ER_GRF_PLNTSTOR ER_H2O_WUEYST ER_MRN_MPA ER_PTD_MTN ER_RDE_OSEX ER_RSK_LST FB_CBK_BRCH FC_ACC_SSID GB_POP_SCIERD GB_XPD_RSDV GC_TAX_TOTL_GD_ZS IS_RDP_PFVOL IT_MOB_2GNTWK IT_MOB_OWN IT_USE_ii99 NV_IND_MANF NV_IND_TECH NY_GDP_MKTP_KD_ZG NY_GDP_PCAP SD_XPD_ESED SE_ACS_ELECT SE_ACS_H2O SE_ACS_INTNT SE_ADT_EDUCTRN SE_ADT_LITR SE_GPI_PART SE_GPI_PTNPRE SE_PRE_PARTN SE_TOT_PRFL SE_TRA_GRDL SG_GEN_PARL SG_HAZ_CMRBASEL SG_HAZ_CMRROTDAM SG_PLN_PRVNDI SG_PLN_RECNDI SG_PLN_RECRIMON SG_REG_BRTH SG_STT_CAPTY SH_ACS_DTP3 SH_FPL_MTMM SH_H2O_SAFE SH_IHR_CAPS SH_MED_DEN SH_SAN_SAFE SI_COV_BENFTS SI_COV_PENSN SL_EMP_GTOTL SL_EMP_PCAP SP_TRN_PUBL TX_EXP_GBSVR'.split())
SIGNS = {**dict.fromkeys(NEGATIVE,-1), **dict.fromkeys(POSITIVE,1)}
NOTES = {
 'ER_RSK_LST': 'Red List Index: 1 = lowest risk; 0 = extinction. Increase.',
 'SH_SAN_DEFECT': 'Share practising open defecation: decrease; inverse of sanitation coverage.',
 'SH_SAN_SAFE': 'Safely managed sanitation coverage: increase.',
 'SL_TLF_UEM': 'Unemployment: decrease even when used as a proxy for earnings (8.5.1).',
 'AG_LND_FRST': 'Forest area: increase even when used as a proxy for target 15.3; the measure is forest area rather than degraded land.',
 'GB_POP_SCIERD': 'Researchers: increase; the target 12.a proxy measures researchers rather than electricity capacity.',
 'TX_EXP_GBSVR': 'Share of world services exports: increase (17.11.1); replaces the legacy -1. Direction follows the series definition; applicability to developed economies requires separate consideration.',
 'ER_UNK_LBREDN': 'Analytical convention: decrease breeds with unknown risk. This measures an information gap rather than observed extinction risk. This series is not assessed in the UNSD 2026 annex.',
 'AG_LND_FRSTBIOPHA': 'Measure interpretation: increase above-ground biomass per hectare of forest. This is not a deforestation rate. The 2026 annex assesses other components of 15.2.1.',
 'AG_LND_SUST_PRXCSS': 'Sustainable agriculture status score: increase. The 2026 annex uses the trend score; status-score direction is interpreted from its definition.',
 'SE_GPI_PART': 'Project convention retained: increase relative female participation. Values are not transformed into distance from 1.',
 'SE_GPI_PTNPRE': 'Project convention retained: increase relative female participation. Values are not transformed into distance from 1.',
 'SH_IHR_CAPS': 'Interpretation: increase IHR capacities; the supplied 2026 annex has no direction for this series.',
}
SOURCE = 'UNSD, Technical Note for Progress Assessment 2026, series-level annex; explicit interpretation where a series differs or is absent.'
def resolve_api(api):
    if api not in SIGNS:
        return None, 'Unreviewed series: define a specific rule for '+api
    sign = SIGNS[api]
    note = NOTES.get(api, ('Increase' if sign==1 else 'Decrease')+' the observed measure; check the description, dimensions and unit recorded in Series.')
    return sign, SOURCE+' '+note
