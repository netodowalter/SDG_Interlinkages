"""Revisão de sentido por código da série efetivamente usada (2026-11-02).
Base: anexo da Technical Note for Progress Assessment 2026, UNSD,
e definição das medidas. As exceções interpretativas são identificadas.
O sinal multiplica o Pearson; valores originais não são transformados.
"""
NEGATIVE = set('AG_FPA_HMFP DT_TDS_DECT EG_EGY_PRIM EN_ATM_CO2MVA EN_ATM_PM25 EN_LND_SLUM EN_MAT_DOMCMPG EN_MAT_DOMCMPT ER_FFS_CMPT_GDP ER_FFS_CMPT_PC_CD ER_H2O_STRESS ER_UNK_LBREDN IC_FRM_BRIB SH_ALC_CONSPT SH_DTH_NCOM SH_DYN_MORT SH_HIV_INCD SH_OOP_XPD_EARNNET40 SH_PRV_SMOK SH_SAN_DEFECT SH_STA_MALR SH_STA_MORT SH_STA_POISN SH_STA_STNT SH_STA_TRAF SH_STA_WASHARI SH_STA_WAST SH_TBS_INCD SI_POV_DAY1 SI_RMT_COST SL_ISV_IFEM SL_TLF_NEET SL_TLF_UEM SN_ITK_DEFC SP_DYN_ADKL SP_DYN_MRBF15 VC_IHR_PSRC VC_PRS_UNSNT VC_VAW_MARR'.split())
POSITIVE = set('AG_LND_FRST AG_LND_FRSTBIOPHA AG_LND_SUST_PRXCSS AG_PRD_ORTIND BX_TRF_PWKR DC_FTA_TOTAL DC_ODA_BDVL DC_TOF_AGRL DC_TOF_INFRAL DC_TOF_SCHIPSL DC_TOF_TRDDBML DC_TOF_WASHL DC_TRF_TFDV EG_ACS_ELEC EG_EGY_CLEAN EG_FEC_RNEW EN_EWT_RCYV EN_LKRV_PWAP EN_WWT_WWDS ER_GRF_PLNTSTOR ER_H2O_WUEYST ER_MRN_MPA ER_PTD_MTN ER_RDE_OSEX ER_RSK_LST FB_CBK_BRCH FC_ACC_SSID GB_POP_SCIERD GB_XPD_RSDV GC_TAX_TOTL_GD_ZS IS_RDP_PFVOL IT_MOB_2GNTWK IT_MOB_OWN IT_USE_ii99 NV_IND_MANF NV_IND_TECH NY_GDP_MKTP_KD_ZG NY_GDP_PCAP SD_XPD_ESED SE_ACS_ELECT SE_ACS_H2O SE_ACS_INTNT SE_ADT_EDUCTRN SE_ADT_LITR SE_GPI_PART SE_GPI_PTNPRE SE_PRE_PARTN SE_TOT_PRFL SE_TRA_GRDL SG_GEN_PARL SG_HAZ_CMRBASEL SG_HAZ_CMRROTDAM SG_PLN_PRVNDI SG_PLN_RECNDI SG_PLN_RECRIMON SG_REG_BRTH SG_STT_CAPTY SH_ACS_DTP3 SH_FPL_MTMM SH_H2O_SAFE SH_IHR_CAPS SH_MED_DEN SH_SAN_SAFE SI_COV_BENFTS SI_COV_PENSN SL_EMP_GTOTL SL_EMP_PCAP SP_TRN_PUBL TX_EXP_GBSVR'.split())
SIGNS = {**dict.fromkeys(NEGATIVE,-1), **dict.fromkeys(POSITIVE,1)}
NOTES = {
 'ER_RSK_LST': 'Red List Index: 1 = menor risco; 0 = extinção. Aumentar.',
 'SH_SAN_DEFECT': 'Proporção com defecação a céu aberto: reduzir; inversa de cobertura sanitária.',
 'SH_SAN_SAFE': 'Cobertura de saneamento seguro: aumentar.',
 'SL_TLF_UEM': 'Desemprego: reduzir mesmo quando usado como proxy de remuneração (8.5.1).',
 'AG_LND_FRST': 'Área florestal: aumentar mesmo quando usada como proxy da meta 15.3; não é terra degradada.',
 'GB_POP_SCIERD': 'Pesquisadores: aumentar; a proxy da meta 12.a mede pesquisadores, não capacidade elétrica.',
 'TX_EXP_GBSVR': 'Participação nas exportações mundiais de serviços: aumentar (17.11.1); substitui o -1 legado. A direção segue a série; não resolve por si a aplicabilidade da meta a economias desenvolvidas.',
 'ER_UNK_LBREDN': 'Convenção analítica: reduzir raças com risco desconhecido; mede lacuna de informação, não risco observado de extinção. Não consta como série avaliada no anexo UNSD 2026.',
 'AG_LND_FRSTBIOPHA': 'Interpretação da medida: aumentar biomassa acima do solo por hectare de floresta; não é a taxa de desmatamento. O anexo 2026 avalia outros componentes de 15.2.1.',
 'AG_LND_SUST_PRXCSS': 'Escore de situação da agricultura sustentável: aumentar. O anexo 2026 usa o escore de tendência; a direção do escore de situação é interpretada pela definição.',
 'SE_GPI_PART': 'Mantida a convenção do projeto: aumentar participação relativa feminina. Não transforma valores em distância até 1.',
 'SE_GPI_PTNPRE': 'Mantida a convenção do projeto: aumentar participação relativa feminina. Não transforma valores em distância até 1.',
 'SH_IHR_CAPS': 'Interpretação: aumentar capacidades IHR; o sentido está vazio no anexo 2026 fornecido.',
}
SOURCE = 'UNSD, Technical Note for Progress Assessment 2026, anexo por série; interpretação explícita quando a série difere ou está ausente.'
def resolve_api(api):
    if api not in SIGNS:
        return None, 'Série não revisada: definir regra específica para '+api
    sign = SIGNS[api]
    note = NOTES.get(api, ('Aumentar' if sign==1 else 'Reduzir')+' a medida efetivamente observada; conferir descrição, dimensões e unidade registradas em Series.')
    return sign, SOURCE+' '+note
