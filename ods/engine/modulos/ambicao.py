"""Fonte única de ambição por meta: tabela integral fornecida pelo usuário."""
import json
import math
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent/'bases'/'ambicao_metas.json'
DATA=json.loads(BASE.read_text(encoding='utf-8'))
AMBITIONS=DATA['valores']
SOURCE=DATA['fonte']
COUNTS=[7,8,13,10,9,8,5,12,8,10,10,11,5,10,12,12,19]
if len(AMBITIONS)!=169 or any(sum(k.split('.')[0]==str(i) for k in AMBITIONS)!=n for i,n in enumerate(COUNTS,1)):
    raise ValueError('Tabela de ambição incompleta: esperadas as 169 metas ODS.')
if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in AMBITIONS.values()):
    raise ValueError('Ambição deve ser numérica entre 0 e 1, incluindo zero.')
def ambition_for(target):
    if target not in AMBITIONS:raise ValueError('Meta sem ambição cadastrada: '+str(target))
    return AMBITIONS[target]
