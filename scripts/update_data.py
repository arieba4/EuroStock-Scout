from __future__ import annotations
import json, math
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import yfinance as yf
from universe import broad_universe

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"market-data.json"

MARKETS={
 "Europe":{
  "currency":"EUR","benchmark":{"ticker":"EXSA.DE","name":"iShares STOXX Europe 600 UCITS ETF"},
  "stocks":[
   ("Airbus","AIR.PA"),("Schneider Electric","SU.PA"),("LVMH","MC.PA"),("Sanofi","SAN.PA"),("TotalEnergies","TTE.PA"),
   ("BNP Paribas","BNP.PA"),("AXA","CS.PA"),("Vinci","DG.PA"),("L'Oreal","OR.PA"),("Air Liquide","AI.PA"),
   ("EssilorLuxottica","EL.PA"),("Danone","BN.PA"),("Pernod Ricard","RI.PA"),("Bouygues","EN.PA"),("Thales","HO.PA"),
   ("Capgemini","CAP.PA"),("Safran","SAF.PA"),("STMicroelectronics","STMPA.PA"),("Hermes","RMS.PA"),("Publicis Groupe","PUB.PA"),
   ("Siemens","SIE.DE"),("SAP","SAP.DE"),("Allianz","ALV.DE"),("Deutsche Telekom","DTE.DE"),("Mercedes-Benz","MBG.DE"),
   ("BMW","BMW.DE"),("BASF","BAS.DE"),("Infineon","IFX.DE"),("Munich Re","MUV2.DE"),("Deutsche Boerse","DB1.DE"),
   ("Adidas","ADS.DE"),("RWE","RWE.DE"),("E.ON","EOAN.DE"),("Deutsche Bank","DBK.DE"),("Volkswagen Pref","VOW3.DE"),
   ("Henkel Pref","HEN3.DE"),("Beiersdorf","BEI.DE"),("Symrise","SY1.DE"),("Continental","CON.DE"),("DHL Group","DHL.DE"),
   ("ASML","ASML.AS"),("ING","INGA.AS"),("Prosus","PRX.AS"),("Ahold Delhaize","AD.AS"),("Unilever","UNA.AS"),
   ("Heineken","HEIA.AS"),("Philips","PHIA.AS"),("ASM International","ASM.AS"),("Akzo Nobel","AKZA.AS"),("KPN","KPN.AS"),
   ("Iberdrola","IBE.MC"),("Inditex","ITX.MC"),("Banco Santander","SAN.MC"),("BBVA","BBVA.MC"),("Amadeus IT","AMS.MC"),
   ("Telefonica","TEF.MC"),("Enel","ENEL.MI"),("UniCredit","UCG.MI"),("Intesa Sanpaolo","ISP.MI"),("Eni","ENI.MI")
  ]},
 "Canada":{
  "currency":"CAD","benchmark":{"ticker":"XIU.TO","name":"iShares S&P/TSX 60 Index ETF"},
  "stocks":[
   ("Royal Bank of Canada","RY.TO"),("Toronto-Dominion Bank","TD.TO"),("Bank of Montreal","BMO.TO"),("Bank of Nova Scotia","BNS.TO"),
   ("CIBC","CM.TO"),("National Bank of Canada","NA.TO"),("Shopify","SHOP.TO"),("Canadian Natural Resources","CNQ.TO"),
   ("Suncor Energy","SU.TO"),("Enbridge","ENB.TO"),("Canadian Pacific Kansas City","CP.TO"),("Canadian National Railway","CNR.TO"),
   ("Brookfield Corp.","BN.TO"),("Barrick Mining","ABX.TO"),("Constellation Software","CSU.TO"),("Thomson Reuters","TRI.TO"),
   ("Manulife Financial","MFC.TO"),("Sun Life Financial","SLF.TO"),("TC Energy","TRP.TO"),("Nutrien","NTR.TO"),
   ("Waste Connections","WCN.TO"),("Dollarama","DOL.TO"),("Fortis","FTS.TO"),("Alimentation Couche-Tard","ATD.TO"),
   ("Agnico Eagle Mines","AEM.TO"),("BCE","BCE.TO"),("TELUS","T.TO"),("Power Corp. of Canada","POW.TO"),
   ("Great-West Lifeco","GWO.TO"),("Intact Financial","IFC.TO"),("Restaurant Brands International","QSR.TO"),("Cameco","CCO.TO"),
   ("Franco-Nevada","FNV.TO"),("Wheaton Precious Metals","WPM.TO"),("Teck Resources B","TECK-B.TO"),("Imperial Oil","IMO.TO"),
   ("Pembina Pipeline","PPL.TO"),("Keyera","KEY.TO"),("ARC Resources","ARX.TO"),("Tourmaline Oil","TOU.TO"),
   ("Loblaw","L.TO"),("Metro","MRU.TO"),("Empire Company A","EMP-A.TO"),("Canadian Tire A","CTC-A.TO"),
   ("CGI","GIB-A.TO"),("Rogers Communications B","RCI-B.TO"),("Brookfield Infrastructure","BIP-UN.TO"),
   ("Brookfield Asset Management","BAM.TO"),("Canadian Apartment REIT","CAR-UN.TO"),("Capital Power","CPX.TO")
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
    df=yf.Ticker(ticker).history(period="18mo",interval="1d",auto_adjust=True,actions=True,repair=False,raise_errors=False)
    if df is None or df.empty:return None
    idx=pd.to_datetime(df.index)
    if getattr(idx,"tz",None) is not None: idx=idx.tz_localize(None)
    df=df.copy();df.index=idx
    return df.sort_index()

def histories(tickers,chunk_size=40):
    """Download prices in batches to keep a 580-stock workflow practical."""
    result={}
    for start in range(0,len(tickers),chunk_size):
        chunk=tickers[start:start+chunk_size]
        data=yf.download(chunk,period="18mo",interval="1d",auto_adjust=True,actions=True,repair=False,
                         group_by="ticker",threads=True,progress=False)
        for ticker in chunk:
            try:
                df=data[ticker].dropna(how="all") if isinstance(data.columns,pd.MultiIndex) else data.dropna(how="all")
                if df.empty: continue
                idx=pd.to_datetime(df.index)
                if getattr(idx,"tz",None) is not None: idx=idx.tz_localize(None)
                df=df.copy();df.index=idx;result[ticker]=df.sort_index()
            except Exception: continue
    return result

def trailing_dividend_yield(df,price):
    if "Dividends" not in df.columns or not price:return None
    cutoff=pd.Timestamp.utcnow().tz_localize(None)-pd.Timedelta(days=365)
    total=float(df.loc[df.index>=cutoff,"Dividends"].fillna(0).sum())
    return safe(total/price*100)

def pct_return(series, sessions):
    return safe((series.iloc[-1] / series.iloc[-sessions-1] - 1) * 100) if len(series) > sessions else None

def market_regime(bench):
    c=bench["Close"].dropna(); p=safe(c.iloc[-1]); s20=safe(c.tail(20).mean()); s50=safe(c.tail(50).mean()); s200=safe(c.tail(200).mean())
    momentum=pct_return(c,20)
    if p>s20>s50 and p>s200 and momentum>0: label="BULLISH"
    elif p<s20<s50 and p<s200 and momentum<0: label="BEARISH"
    else: label="NEUTRAL"
    return {"label":label,"price":p,"sma20":s20,"sma50":s50,"sma200":s200,"momentum20":momentum}

def analyze(name,ticker,df,bench,currency):
    if df is None or len(df)<210:return {"name":name,"ticker":ticker,"status":"error","error":"insufficient history"}
    c=df["Close"].dropna()
    bd=beta_diag(c,bench["Close"].dropna())
    if not bd:return {"name":name,"ticker":ticker,"status":"error","error":"beta unavailable"}
    price=safe(c.iloc[-1]); a=atr(df)
    if price is None or a is None:return {"name":name,"ticker":ticker,"status":"error","error":"price/ATR unavailable"}
    volume=df["Volume"].fillna(0) if "Volume" in df.columns else pd.Series(dtype=float)
    avg_volume20=safe(volume.tail(20).mean()) if len(volume) else None
    avg_volume60=safe(volume.tail(60).mean()) if len(volume) else None
    current_volume=safe(volume.iloc[-1]) if len(volume) else None
    avg_traded=safe((df["Close"].tail(20)*volume.tail(20)).mean()) if len(volume) else None
    bench_close=bench["Close"].dropna()
    ret20=pct_return(c,20); ret60=pct_return(c,60)
    bench20=pct_return(bench_close,20); bench60=pct_return(bench_close,60)
    support20=safe(df["Low"].tail(20).min()); support50=safe(df["Low"].tail(50).min())
    resistance20=safe(df["High"].tail(20).max()); resistance50=safe(df["High"].tail(50).max())
    result={"name":name,"ticker":ticker,"currency":currency,"status":"ok","price":price,
            "sma20":safe(c.tail(20).mean()),"sma50":safe(c.tail(50).mean()),
            "sma200":safe(c.tail(200).mean()),
            "rsi":safe(rsi(c)),"momentum20":safe((c.iloc[-1]/c.iloc[-21]-1)*100 if len(c)>21 else None),
            "atr":a,"atrPct":safe(a/price*100),"dividendYield":trailing_dividend_yield(df,price),
            "avgVolume20":avg_volume20,"avgVolume60":avg_volume60,"currentVolume":current_volume,
            "avgTradedValue20":avg_traded,"volumeRatio":safe(current_volume/avg_volume20 if avg_volume20 else None),
            "return20":ret20,"return60":ret60,
            "benchmarkReturn20":bench20,"benchmarkReturn60":bench60,
            "relativeStrength20":safe(ret20-bench20 if ret20 is not None and bench20 is not None else None),
            "relativeStrength60":safe(ret60-bench60 if ret60 is not None and bench60 is not None else None),
            "support20":support20,"support50":support50,"resistance20":resistance20,"resistance50":resistance50,
            "distanceToSupportPct":safe((price-support20)/price*100),
            "distanceToResistancePct":safe((resistance20-price)/price*100),
            "distanceFromSma200Pct":None}
    result["distanceFromSma200Pct"]=safe((price-result["sma200"])/result["sma200"]*100 if result["sma200"] else None)
    result.update(bd)
    if any(result[k] is None for k in ["sma20","sma50","sma200","rsi","momentum20","avgTradedValue20","volumeRatio","relativeStrength20"]):
        return {"name":name,"ticker":ticker,"status":"error","error":"indicator unavailable"}
    min_traded=5_000_000
    result["liquid"]=bool(result["avgTradedValue20"]>=min_traded)
    result["eligible"]=result["liquid"]
    result["interesting"]=bool(result["eligible"] and price>=result["sma200"]*.92 and result["relativeStrength20"]>=-5)
    return result

def next_earnings(ticker):
    try:
        dates=yf.Ticker(ticker).get_earnings_dates(limit=4)
        if dates is None or dates.empty:return None
        now=pd.Timestamp.now(tz="UTC")
        idx=pd.to_datetime(dates.index,utc=True)
        future=idx[idx>=now]
        return future[0].isoformat() if len(future) else None
    except Exception:return None

def main():
    payload={"schema":2,"generated_at":datetime.now(timezone.utc).isoformat(),"source":"yfinance via GitHub Actions","markets":{}}
    core={market:list(cfg["stocks"]) for market,cfg in MARKETS.items()}
    universe,warnings=broad_universe(core)
    payload["universe_warnings"]=warnings
    for market,cfg in MARKETS.items():
        print(f"Updating {market}...")
        bench=history(cfg["benchmark"]["ticker"])
        if bench is None or len(bench)<60:
            raise RuntimeError(f"Benchmark failed: {cfg['benchmark']['ticker']}")
        members=universe[market]
        downloaded=histories([ticker for _,ticker,_ in members])
        stocks=[]
        for i,(name,ticker,currency) in enumerate(members,1):
            print(f"  {i}/{len(members)} {ticker}")
            try:
                stocks.append(analyze(name,ticker,downloaded.get(ticker),bench,currency))
            except Exception as e:
                stocks.append({"name":name,"ticker":ticker,"status":"error","error":str(e)})
        candidates=[x for x in stocks if x.get("interesting")]
        with ThreadPoolExecutor(max_workers=8) as pool:
            jobs={pool.submit(next_earnings,x["ticker"]):x for x in candidates}
            for job in as_completed(jobs): jobs[job]["nextEarnings"]=job.result()
        now=datetime.now(timezone.utc)
        for x in stocks:
            event=None; days=None
            if x.get("nextEarnings"):
                days=(datetime.fromisoformat(x["nextEarnings"])-now).days
                event=days<=7
            x["daysToEarnings"]=days; x["eventRisk"]=bool(event)
        counts={"universe":len(stocks),"dataQuality":sum(x.get("status")=="ok" for x in stocks),"eligible":sum(x.get("eligible",False) for x in stocks),"interesting":sum(x.get("interesting",False) for x in stocks)}
        payload["markets"][market]={"currency":cfg["currency"],"benchmark":{**cfg["benchmark"],"observations":int(len(bench)),"regime":market_regime(bench)},"funnel":counts,"stocks":stocks}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,allow_nan=False),encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__=="__main__":
    main()
