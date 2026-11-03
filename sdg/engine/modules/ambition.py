'Single source of target ambition: the complete user-supplied table.'
import json
import math
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent/'bases'/'target_ambition.json'
DATA=json.loads(BASE.read_text(encoding='utf-8'))
AMBITIONS=DATA['values']
SOURCE=DATA['source']
COUNTS=[7,8,13,10,9,8,5,12,8,10,10,11,5,10,12,12,19]
if len(AMBITIONS)!=169 or any(sum(k.split('.')[0]==str(i) for k in AMBITIONS)!=n for i,n in enumerate(COUNTS,1)):
    raise ValueError('Incomplete ambition table: all 169 SDG targets are required.')
if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in AMBITIONS.values()):
    raise ValueError('Ambition must be numeric between 0 and 1, including zero.')
def ambition_for(target):
    if target not in AMBITIONS:raise ValueError('No ambition recorded for target: '+str(target))
    return AMBITIONS[target]
