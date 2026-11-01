import re,glob,sys,os
KW={'ITSA':['Itaúsa','Itausa'],'LREN':['Renner'],'BRML':['BR Malls','BRMalls'],'CIEL':['Cielo'],'BVMF':['BM&F','BMF','Bovespa','B3 ','BVMF'],'KROT':['Kroton'],'VALE':['Vale '],'GGBR':['Gerdau'],'ABEV':['Ambev','AmBev'],
'CYRE':['Cyrela'],'BBSE':['BB Seguridade','Seguridade'],'WEGE':['WEG'],'VIVT':['Telefônica','Vivo'],'ITUB':['Itaú ','Itaú,','Itaú.'],'CSAN':['Cosan'],'SUZB':['Suzano'],'CMIG':['Cemig'],'STBP':['Santos Brasil'],'GNDI':['Intermédica','Intermedica','NotreDame'],
'HGTX':['Hering'],'NATU':['Natura'],'MGLU':['Magazine','Magalu'],'SCAR':['São Carlos','Sao Carlos'],'RUMO':['Rumo'],'RAIL':['Rumo'],'SSBR':['Sierra'],'POMO':['Marcopolo'],'BRPR':['BR Properties'],'RAPT':['Randon'],'UGPA':['Ultrapar','Ultra '],
'ALSC':['Aliansce'],'BRKM':['Braskem'],'LOGN':['Log-In','Log-in'],'ARZZ':['Arezzo'],'FIBR':['Fibria'],'PETR':['Petrobras'],'VLID':['Valid'],'IGTA':['Iguatemi'],'CGAS':['Comgás','Comgas'],'RLOG':['Cosan Log'],'CVCB':['CVC'],'EMBR':['Embraer'],'DAGB':['Dufry'],
'EQTL':['Equatorial'],'HYPE':['Hypera','Hypermarcas'],'BBDC':['Bradesco'],'ESTC':['Estácio','Estacio'],'ENGI':['Energisa'],'SEER':['Ser Educacional'],'QUAL':['Qualicorp'],'LAME':['Lojas Americanas','Americanas'],'TRPL':['Transmissão Paulista','CTEEP','ISA CTEEP'],
'BRAP':['Bradespar'],'CTIP':['Cetip'],'BRFS':['BRF'],'QGEP':['QGEP'],'MULT':['Multiplan'],'CSMG':['Copasa'],'VVAR':['Via Varejo'],'PCAR':['Pão de Açúcar','GPA'],'ELET':['Eletrobras','Eletrobrás'],'BBAS':['Banco do Brasil'],'ELPL':['Eletropaulo'],
'CESP':['Cesp','CESP'],'BBTG':['BTG'],'HAPV':['Hapvida'],'JSLG':['JSL'],'GOAU':['Metalúrgica Gerdau','Gerdau'],'VULC':['Vulcabras'],'MOVI':['Movida'],'LLIS':['Le Lis','Restoque'],'ANIM':['Anima','Ânima'],'DTEX':['Duratex'],'MAGG':['Magnesita'],
'TPIS':['Triunfo'],'CPFE':['CPFL'],'ALPA':['Alpargatas'],'BIDI':['Banco Inter'],'FLRY':['Fleury'],'ABRE':['Abril Educação','Somos'],'SEDU':['Somos'],'ENBR':['EDP','Energias do Brasil'],'GUAR':['Guararapes','Riachuelo'],'WIZS':['Wiz'],'PARC':['Par Corretora'],
'B3SA':['B3 '],'JBSS':['JBS'],'RENT':['Localiza'],'RADL':['Raia'],'SAPR':['Sanepar'],'SBSP':['Sabesp'],'TAEE':['Taesa'],'TIMP':['TIM'],'MDIA':['M. Dias','M.Dias'],'LINX':['Linx'],'TOTS':['Totvs','TOTVS']}
def paras(t):
    t=re.sub(r'[ \t]+',' ',t); ps=[p.strip() for p in re.split(r'\n\s*\n',t) if len(p.strip())>120]
    return ps
out=[]
for f in sorted(glob.glob(sys.argv[1])):
    t=open(f,errors='ignore').read(); ps=paras(t)
    sc=[]
    for p in ps:
        hits={k for k,ws in KW.items() if any(w in p for w in ws)}
        if hits: sc.append((len(hits)+ (2 if re.search(r'(compr|vend|posi|tese|investimos|aument|reduz|zeramos|carteira)',p,re.I) else 0),p,hits))
    sc.sort(key=lambda x:-x[0]); tot=0; sel=[]
    for s,p,h in sc:
        if tot>int(os.environ.get("CAP","2600")): break
        p=re.sub(r'\s*\n\s*',' ',p); sel.append(p[:1300]); tot+=len(p[:1300])
    out.append(f"##### {os.path.basename(f)}\n"+"\n---\n".join(sel))
print('\n\n'.join(out))
