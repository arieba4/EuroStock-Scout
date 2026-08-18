from __future__ import annotations
import json, math, time
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import yfinance as yf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"market-data.json"

MARKETS={
 "Europe":{
  "currency":"EUR","benchmark":{"ticker":"EXSA.DE","name":"iShares STOXX Europe 600 UCITS ETF"},
  "stocks":[
   ("Airbus","AIR.PA"),("Schneider Electric","SU.PA"),("LVMH","MC.PA"),("Sanofi","SAN.PA"),
   ("TotalEnergies","TTE.PA"),("BNP Paribas","BNP.PA"),("AXA","CS.PA"),("Vinci","DG.PA"),
   ("Siemens","SIE.DE"),("SAP","SAP.DE"),("Allianz","ALV.DE"),("Deutsche Telekom","DTE.DE"),
   ("Mercedes-Benz","MBG.DE"),("BMW","BMW.DE"),("BASF","BAS.DE"),("Infineon","IFX.DE"),
   ("ASML","ASML.AS"),("ING","INGA.AS"),("Prosus","PRX.AS"),("Ahold Delhaize","AD.AS"),
   ("Iberdrola","IBE.MC"),("Inditex","ITX.MC"),("Enel","ENEL.MI"),("UniCredit","UCG.MI")
  ]},
 "Canada":{
  "currency":"CAD","benchmark":{"ticker":"XIU.TO","name":"iShares S&P/TSX 60 Index ETF"},
  "stocks":[
   ("Royal Bank of Canada","RY.TO"),("Toronto-Dominion Bank","TD.TO"),("Bank of Montreal","BMO.TO"),("Bank of Nova Scotia","BNS.TO"),
   ("CIBC","CM.TO"),("National Bank of Canada","NA.TO"),("Shopify","SHOP.TO"),("Canadian Natural Resources","CNQ.TO"),
   ("Suncor Energy","SU.TO"),("Enbridge","ENB.TO"),("Canadian Pacific Kansas City","CP.TO"),("Canadian National Railway","CNR.TO"),
   ("Brookfield Corp.","BN.TO"),("Barrick Mining","ABX.TO"),("Constellation Software","CSU.TO"),("Thomson Reuters","TRI.TO"),
   ("Manulife Financial","MFC.TO"),("Sun Life Financial","SLF.TO"),("TC Energy","TRP.TO"),("Nutrien","NTR.TO"),
   ("Waste Connections","WCN.TO"),("Dollarama","DOL.TO"),("Fortis","FTS.TO"),("Alimentation Couche-Tard","ATD.TO")
  ]}
}

def safe(x):
    if x is None or (isinstance(x,float) and (math.isnan(x) or math.isinf(x))): return None
    return float(x)

def rsi(c,n=14):
    d=c.diff().dropna()
    if len(d)<n:return None
    g=d.clip(lower=0).tail(n).mean(); l=(-d.clip(upper=0)).tail(n).mean()
    return 100.0 if l==0 else 100-(100/(1+g/l))

def atr(df,n=14):
    if len(df)<n+1:return None
    pc=df["Close"].shift(1)
    tr=pd.concat([(df["High"]-df["Low"]).abs(),(df["High"]-pc).abs(),(df["Low"]-pc).abs()],axis=1).max(axis=1)
    return safe(tr.tail(n).mean())

def beta_diag(stock_close, bench_close):
    s=stock_close.pct_change().rename("s"); b=bench_close.pct_change().rename("b")
    a=pd.concat([s,b],axis=1).dropna()
    if len(a)<60:return None
    cov=a["s"].cov(a["b"]); var=a["b"].var()
    if not var:return None
    sv=a["s"].std()*math.sqrt(252)*100; bv=a["b"].std()*math.sqrt(252)*100
    corr=a["s"].corr(a["b"])
    return {"beta":safe(cov/var),"betaObs":int(len(a)),"correlation":safe(corr),"stockVol":safe(sv),"benchmarkVol":safe(bv),"volRatio":safe(sv/bv if bv else None)}

def history(ticker):
    df=yf.Ticker(ticker).history(period="18mo",interval="1d",auto_adjust=True,actions=True,repair=True,raise_errors=False)
    if df is None or df.empty:return None
    idx=pd.to_datetime(df.index)
    if getattr(idx,"tz",None) is not None: idx=idx.tz_localize(None)
    df=df.copy();df.index=idx
    return df.sort_index()

def trailing_dividend_yield(df,price):
    if "Dividends" not in df.columns or not price:return None
    cutoff=pd.Timestamp.utcnow().tz_localize(None)-pd.Timedelta(days=365)
    total=float(df.loc[df.index>=cutoff,"Dividends"].fillna(0).sum())
    return safe(total/price*100)

def analyze(name,ticker,df,bench,currency):
    if df is None or len(df)<60:return {"name":name,"ticker":ticker,"status":"error","error":"insufficient history"}
    c=df["Close"].dropna()
    bd=beta_diag(c,bench["Close"].dropna())
    if not bd:return {"name":name,"ticker":ticker,"status":"error","error":"beta unavailable"}
    price=safe(c.iloc[-1]); a=atr(df)
    if price is None or a is None:return {"name":name,"ticker":ticker,"status":"error","error":"price/ATR unavailable"}
    result={"name":name,"ticker":ticker,"currency":currency,"status":"ok","price":price,
            "sma20":safe(c.tail(20).mean()),"sma50":safe(c.tail(50).mean()),
            "rsi":safe(rsi(c)),"momentum20":safe((c.iloc[-1]/c.iloc[-21]-1)*100 if len(c)>21 else None),
            "atr":a,"atrPct":safe(a/price*100),"dividendYield":trailing_dividend_yield(df,price)}
    result.update(bd)
    if any(result[k] is None for k in ["sma20","sma50","rsi","momentum20"]):
        return {"name":name,"ticker":ticker,"status":"error","error":"indicator unavailable"}
    return result

def main():
    payload={"schema":1,"generated_at":datetime.now(timezone.utc).isoformat(),"source":"yfinance via GitHub Actions","markets":{}}
    for market,cfg in MARKETS.items():
        print(f"Updating {market}...")
        bench=history(cfg["benchmark"]["ticker"])
        if bench is None or len(bench)<60:
            raise RuntimeError(f"Benchmark failed: {cfg['benchmark']['ticker']}")
        stocks=[]
        for i,(name,ticker) in enumerate(cfg["stocks"],1):
            print(f"  {i}/{len(cfg['stocks'])} {ticker}")
            try:
                df=history(ticker)
                stocks.append(analyze(name,ticker,df,bench,cfg["currency"]))
            except Exception as e:
                stocks.append({"name":name,"ticker":ticker,"status":"error","error":str(e)})
            time.sleep(.15)
        payload["markets"][market]={"currency":cfg["currency"],"benchmark":{**cfg["benchmark"],"observations":int(len(bench))},"stocks":stocks}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,allow_nan=False),encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__=="__main__":
    main()
