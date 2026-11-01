import pandas as pd, re, sys
from openpyxl import load_workbook
W,OUT=sys.argv[1],sys.argv[2]
P=pd.read_pickle(W+'/pairs.pkl')
EXC=r'ITA[UÚ]|OPPORTUNITY|\bXP\b|BRADESCO|BRAM|SANTANDER|AZ QUEST|BTG|SAFRA|\bBB\b|CAIXA|VERDE|RPS|ARX|PAC[IÍ]FICO|VINCI|GENIAL|PLURAL'
def sn(n):
    n=re.sub(r'(-\s*)?FUNDO DE INVESTIMENTO(S)? EM COTAS DE FUNDOS DE INVESTIMENTO( EM| DE)?( A[CÇ][OÕ]ES)?|(-\s*)?FUNDO DE INVESTIMENTO(S)?( EM| DE)?( A[CÇ][OÕ]ES| MULTIMERCADO)?|BDR N[IÍ]VEL\s+I|INVESTIMENTO NO EXTERIOR','',str(n))
    return re.sub(r'\s+',' ',n).strip(' -').title()
x=P[(P.rk14<=50)|(P.rk18<=50)].copy()
x=x[~(x.gestor_18.fillna('')+' '+x.nome_18.fillna('')+' '+x.nome_14.fillna('')).str.upper().str.contains(EXC,regex=True)]
x['Grupo']=x.apply(lambda r:'Top 30 em 2018' if r.rk18<=30 else ('Top 30 em 2014' if r.rk14<=30 else 'Entre 31º e 50º'),axis=1)
x=x.sort_values('rk18')
nm=x.nome_18.where(x.nome_18.notna(),x.nome_14).apply(sn)
nm[x.r18=='29.994.412/0001-76']='Neo Future'
nm[x.r18=='09.271.730/0001-00']='Jgp Equity Master (Multimercado)'
nm[x.r18=='13.136.966/0001-00']='Jgp Equity Explorer Master (Ações)'
nm=nm.str.replace(' Cotas De','')
g=x.gestor_18.str.replace(r'\s*(-\s*)?(GEST(Ã|A)O|GESTORA|ADMINISTRA|INVESTIMENTOS|ASSET MANAGEMENT|CAPITAL LTDA|LTDA|S\.A\.|S/A|PARTNERS).*$','',regex=True).str.title()
out=pd.DataFrame({'#':range(1,len(x)+1),'Fundo':nm.values,'Gestora':g.values,'Grupo':x.Grupo.values,'Rank 2014':x.rk14.values,'Rank 2018':x.rk18.values,
 'PL dez/2014 (R$ mi)':(x.PL_14/1e6).round(0).values,'PL dez/2018 (R$ mi)':(x.PL_18/1e6).round(0).values,
 'Expos. líq. 2014':x.net_14.round(2).values,'Expos. líq. 2018':x.net_18.round(2).values,'CNPJ master 2014':x.r14.values,'CNPJ master 2018':x.r18.values})
with pd.ExcelWriter(OUT,engine='openpyxl',mode='a',if_sheet_exists='replace') as w:
    out.to_excel(w,sheet_name='Lista final',index=False)
    ws=w.sheets['Lista final']
    for c,wd in zip('ABCDEFGHIJKL',[4,34,22,16,9,9,12,12,10,10,20,20]): ws.column_dimensions[c].width=wd
wb=load_workbook(OUT); wb.move_sheet('Lista final',offset=-(len(wb.sheetnames)-1)); wb.save(OUT)
print(out[['#','Fundo','Gestora','Grupo','Rank 2014','Rank 2018','PL dez/2014 (R$ mi)','PL dez/2018 (R$ mi)']].to_string(index=False))
