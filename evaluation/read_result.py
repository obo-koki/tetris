import os
import json
import pandas as pd
from pathlib import Path

# df = pd.DataFrame(columns=['branch','level','time','block','interval','seed','num',
#                             'score','block_index','elapsed_time',
#                             'line','gameover_count','line1','line2','line3','line4']
#                             )
path = Path('./result/')
for ii,file in enumerate(path.glob('*.json')):
    username,branch,mode,level,time,block,interval,seed,num = file.stem.split('_')
    f = open(file, 'r')
    print('reading : '+str(file))
    jsdic=json.load(f)
    df2 = pd.DataFrame({'num':num,
                        'user':username,
                        'branch':[branch],
                        'mode':[mode],
                        'level':level,
                        'time':time,
                        'block':block,
                        'interval':interval,
                        'seed':jsdic['debug_info']['random_seed'],
                        'mode':jsdic['judge_info']['mode'],
                        'score':jsdic['judge_info']['score'],
                        'block_index':jsdic['judge_info']['block_index'],
                        'block_num_max':jsdic['judge_info']['block_num_max'],
                        'elapsed_time':jsdic['judge_info']['elapsed_time'],
                        'game_time':jsdic['judge_info']['game_time'],
                        'line':jsdic['judge_info']['line'],
                        'gameover_count':jsdic['judge_info']['gameover_count'],
                        'line1':jsdic['debug_info']['line_score_stat'][0],
                        'line2':jsdic['debug_info']['line_score_stat'][1],
                        'line3':jsdic['debug_info']['line_score_stat'][2],
                        'line4':jsdic['debug_info']['line_score_stat'][3]})
    # print(df2)
    if ii==0 :
        df = df2
    else:
        df = pd.concat([df,df2])

print("Saving to result.csv")
df.reset_index(drop=True, inplace=True)
df.to_csv('result/result.csv',index = False)
