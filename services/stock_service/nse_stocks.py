"""
NSE (National Stock Exchange of India) Stock List

This module provides a comprehensive list of stocks traded on NSE.
Includes Nifty 50, Nifty Next 50, Nifty 100, and other major stocks.
"""

# Nifty 50 Stocks (as of 2024)
NIFTY_50 = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BPCL",
    "BHARTIARTL", "BRITANNIA", "CIPLA", "COALINDIA", "DRREDDY",
    "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",
    "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK",
    "INFY", "ITC", "JSWSTEEL", "KOTAKBANK", "LT",
    "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC",
    "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SHRIRAMFIN",
    "SUNPHARMA", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TCS",
    "TECHM", "TITAN", "TRENT", "ULTRACEMCO", "WIPRO",
]

# Nifty Next 50 Stocks
NIFTY_NEXT_50 = [
    "ABB", "ACC", "ADANIGREEN", "ADANIPOWER", "AMBUJACEM",
    "AUROPHARMA", "BAJAJHLDNG", "BANKBARODA", "BERGEPAINT", "BOSCHLTD",
    "CANBK", "CHOLAFIN", "COLPAL", "CONCOR", "DABUR",
    "DLF", "GAIL", "GODREJCP", "HAVELLS", "HINDPETRO",
    "ICICIPRULI", "ICICIGI", "IDEA", "IGL", "INDHOTEL",
    "INDUSTOWER", "IOC", "IRCTC", "JINDALSTEL", "JIOFIN",
    "LICI", "LODHA", "LUPIN", "MARICO", "MOTHERSON",
    "MUTHOOTFIN", "NAUKRI", "PEL", "PETRONET", "PGHH",
    "PIDILITIND", "PNB", "RECLTD", "SBICARD", "SIEMENS",
    "SRF", "TORNTPHARM", "TVSMOTOR", "UNIONBANK", "VBL",
    "VEDL", "VOLTAS", "ZOMATO", "ZYDUSLIFE",
]

# Other Popular NSE Stocks (Mid Cap, Small Cap, Sector Leaders)
OTHER_NSE_STOCKS = [
    # IT & Tech
    "MPHASIS", "LTIM", "PERSISTENT", "COFORGE", "MINDTREE",
    "LTTS", "TATAELXSI", "HAPPSTMNDS", "CYIENT", "SONATSOFTW",
    
    # Banks & Finance
    "IDFCFIRSTB", "FEDERALBNK", "RBLBANK", "BANDHANBNK", "AUBANK",
    "MANAPPURAM", "LICHSGFIN", "CANFINHOME", "PNBHOUSING", "AAVAS",
    "CREDITACC", "FINPIPE", "UJJIVANSFB", "EQUITASBNK", "SURYODAY",
    
    # Pharma & Healthcare
    "BIOCON", "ALKEM", "TORNTPOWER", "GLENMARK", "NATCOPHARM",
    "IPCALAB", "LAURUSLABS", "DIVISLAB", "AARTIDRUGS", "GRANULES",
    "FORTIS", "MAXHEALTH", "METROPOLIS", "LALPATHLAB", "THYROCARE",
    
    # Auto & Auto Ancillary
    "ASHOKLEY", "BHARATFORG", "EXIDEIND", "AMARAJABAT", "BALKRISIND",
    "MRF", "APOLLOTYRE", "CEATLTD", "ENDURANCE", "SUNDRMFAST",
    "TUBE", "BOSCHLTD", "MOTHERSON", "VARROC", "SUPRAJIT",
    
    # FMCG & Consumer
    "EMAMILTD", "GODREJCP", "COLPAL", "TATACONSUM", "JUBLFOOD",
    "DMART", "PAGEIND", "VBL", "UNITDSPR", "RADICO",
    "BECTORS", "PATANJALI", "VSTIND", "GODFRYPHLP",
    
    # Infrastructure & Construction
    "LTINFRA", "NBCC", "IRB", "PNC", "ASHOKA",
    "KNRCON", "HCC", "NCC", "JKCEMENT", "RAMCOCEM",
    "DALBHARAT", "SHREECEM", "ORIENTCEM", "HEIDELBERG",
    
    # Power & Energy
    "TATAPOWER", "ADANIGREEN", "ADANIENSOL", "JPPOWER", "NHPC",
    "SJVN", "CESC", "TORNTPOWER", "JSL", "JSWENERGY",
    "IREDA", "PTC", "IEX", "RENUKA",
    
    # Oil & Gas
    "CASTROLIND", "GSPL", "AEGISCHEM", "GUJGASLTD", "MGL",
    "ATGL", "ONGC", "OIL", "MRPL", "CHENNPETRO",
    
    # Metal & Mining
    "NMDC", "MOIL", "NATIONALUM", "HINDZINC", "APLAPOLLO",
    "RATNAMANI", "WELCORP", "SAIL", "TATAMETALI", "JSL",
    
    # Cement
    "ULTRACEMCO", "AMBUJACEM", "ACC", "SHREECEM", "DALBHARAT",
    "RAMCOCEM", "BIRLASOFT", "JKCEMENT", "PRSMJOHNSN", "ORIENTCEM",
    
    # Real Estate
    "DLF", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "BRIGADE",
    "SOBHA", "MAHLIFE", "SUNTECK", "ARVIND", "PHOENIXLTD",
    
    # Chemicals
    "PIDILITIND", "SRF", "ATUL", "NAVINFLUOR", "DEEPAKFERT",
    "GNFC", "GUJALKALI", "TATACHEM", "ROSSARI", "GALAXYSURF",
    "AARTIIND", "VINATIORG", "FINEORG", "CLEAN", "ANURAS",
    
    # Telecom
    "BHARTIARTL", "IDEA", "TATACOMM", "ROUTE", "STLTECH",
    "HFCL", "TEJAS", "GTLINFRA", "ONMOBILE",
    
    # Media & Entertainment
    "ZEEL", "PVRINOX", "SUNTV", "NETWORK18", "TV18BRDCST",
    "DISHTV", "SAREGAMA", "TIPS", "NAZARA",
    
    # Aviation & Logistics
    "INTERGLOBE", "SPICEJET", "BLUEDART", "DELHIVERY", "MAHLOG",
    "TCI", "ALLCARGO", "GATEWAY", "VRL",
    
    # Hotels & Tourism
    "INDHOTEL", "EIHLTD", "LEMONTREE", "CHALET", "MAHINDCIE",
    "TRENDYNT", "THOMASCOOK", "YATRA",
    
    # Textiles
    "ARVIND", "RAYMOND", "VARDHMAN", "TRIDENT", "WELSPUNIND",
    "HIMATSINGKA", "KPRMILL", "PGHL", "RUPA",
    
    # Sugar
    "BALRAMCHIN", "RENUKA", "TRIVENI", "DWARIKESH", "EID",
    "SHAKTISUG", "DHAMPURSUG", "DHAMPUR",
    
    # Paper
    "TNPL", "JKPAPER", "ANDHRAPAP", "STARPAPER", "SESHASAYEE",
    
    # Fertilizers
    "COROMANDEL", "GSFC", "NFL", "GNFC", "FACT",
    "ZUARI", "CHAMBALFERT", "RCF", "SPIC",
    
    # Insurance
    "HDFCLIFE", "ICICIPRULI", "SBILIFE", "LICI", "ICICIGI",
    "STARHEALTH", "NIACL", "GICRE",
    
    # PSU & Defence
    "HAL", "BEL", "BHEL", "BDL", "MAZAGON",
    "COCHINSHIP", "GRSE", "IRFC", "RVNL", "RAILTEL",
    "IRCON", "RITES", "BEML", "MIDHANI",
    
    # Miscellaneous
    "ZOMATO", "PAYTM", "NYKAA", "POLICYBZR", "CARTRADE",
    "EASEMYTRIP", "RATEGAIN", "DREAMFOLK", "MAPMYINDIA",
    "DELHIVERY", "TRACXN", "KAYNES", "CAMPUS",
]

# Complete NSE stocks list with .NS suffix
def get_all_nse_symbols() -> list[str]:
    """Get all NSE stock symbols with .NS suffix."""
    all_stocks = set(NIFTY_50 + NIFTY_NEXT_50 + OTHER_NSE_STOCKS)
    return [f"{symbol}.NS" for symbol in sorted(all_stocks)]

# Stock name mapping (symbol -> company name)
NSE_STOCK_NAMES = {
    # Nifty 50
    "ADANIENT": "Adani Enterprises Ltd",
    "ADANIPORTS": "Adani Ports and SEZ Ltd",
    "APOLLOHOSP": "Apollo Hospitals Enterprise Ltd",
    "ASIANPAINT": "Asian Paints Ltd",
    "AXISBANK": "Axis Bank Ltd",
    "BAJAJ-AUTO": "Bajaj Auto Ltd",
    "BAJFINANCE": "Bajaj Finance Ltd",
    "BAJAJFINSV": "Bajaj Finserv Ltd",
    "BEL": "Bharat Electronics Ltd",
    "BPCL": "Bharat Petroleum Corporation Ltd",
    "BHARTIARTL": "Bharti Airtel Ltd",
    "BRITANNIA": "Britannia Industries Ltd",
    "CIPLA": "Cipla Ltd",
    "COALINDIA": "Coal India Ltd",
    "DRREDDY": "Dr. Reddy's Laboratories Ltd",
    "EICHERMOT": "Eicher Motors Ltd",
    "GRASIM": "Grasim Industries Ltd",
    "HCLTECH": "HCL Technologies Ltd",
    "HDFCBANK": "HDFC Bank Ltd",
    "HDFCLIFE": "HDFC Life Insurance Company Ltd",
    "HEROMOTOCO": "Hero MotoCorp Ltd",
    "HINDALCO": "Hindalco Industries Ltd",
    "HINDUNILVR": "Hindustan Unilever Ltd",
    "ICICIBANK": "ICICI Bank Ltd",
    "INDUSINDBK": "IndusInd Bank Ltd",
    "INFY": "Infosys Ltd",
    "ITC": "ITC Ltd",
    "JSWSTEEL": "JSW Steel Ltd",
    "KOTAKBANK": "Kotak Mahindra Bank Ltd",
    "LT": "Larsen & Toubro Ltd",
    "M&M": "Mahindra & Mahindra Ltd",
    "MARUTI": "Maruti Suzuki India Ltd",
    "NESTLEIND": "Nestle India Ltd",
    "NTPC": "NTPC Ltd",
    "ONGC": "Oil and Natural Gas Corporation Ltd",
    "POWERGRID": "Power Grid Corporation of India Ltd",
    "RELIANCE": "Reliance Industries Ltd",
    "SBILIFE": "SBI Life Insurance Company Ltd",
    "SBIN": "State Bank of India",
    "SHRIRAMFIN": "Shriram Finance Ltd",
    "SUNPHARMA": "Sun Pharmaceutical Industries Ltd",
    "TATACONSUM": "Tata Consumer Products Ltd",
    "TATAMOTORS": "Tata Motors Ltd",
    "TATASTEEL": "Tata Steel Ltd",
    "TCS": "Tata Consultancy Services Ltd",
    "TECHM": "Tech Mahindra Ltd",
    "TITAN": "Titan Company Ltd",
    "TRENT": "Trent Ltd",
    "ULTRACEMCO": "UltraTech Cement Ltd",
    "WIPRO": "Wipro Ltd",
    
    # Major Others
    "ADANIGREEN": "Adani Green Energy Ltd",
    "ADANIPOWER": "Adani Power Ltd",
    "ACC": "ACC Ltd",
    "AMBUJACEM": "Ambuja Cements Ltd",
    "AUROPHARMA": "Aurobindo Pharma Ltd",
    "BANKBARODA": "Bank of Baroda",
    "BERGEPAINT": "Berger Paints India Ltd",
    "BIOCON": "Biocon Ltd",
    "BOSCHLTD": "Bosch Ltd",
    "CANBK": "Canara Bank",
    "CHOLAFIN": "Cholamandalam Investment and Finance Co Ltd",
    "COLPAL": "Colgate-Palmolive India Ltd",
    "DABUR": "Dabur India Ltd",
    "DLF": "DLF Ltd",
    "DMART": "Avenue Supermarts Ltd (DMart)",
    "DIVISLAB": "Divi's Laboratories Ltd",
    "GAIL": "GAIL India Ltd",
    "GODREJCP": "Godrej Consumer Products Ltd",
    "GODREJPROP": "Godrej Properties Ltd",
    "HAL": "Hindustan Aeronautics Ltd",
    "HAVELLS": "Havells India Ltd",
    "HINDPETRO": "Hindustan Petroleum Corporation Ltd",
    "ICICIGI": "ICICI Lombard General Insurance Co Ltd",
    "ICICIPRULI": "ICICI Prudential Life Insurance Co Ltd",
    "IDEA": "Vodafone Idea Ltd",
    "IGL": "Indraprastha Gas Ltd",
    "INDHOTEL": "Indian Hotels Company Ltd",
    "INDUSTOWER": "Indus Towers Ltd",
    "IOC": "Indian Oil Corporation Ltd",
    "IRCTC": "Indian Railway Catering and Tourism Corporation Ltd",
    "JINDALSTEL": "Jindal Steel & Power Ltd",
    "JIOFIN": "Jio Financial Services Ltd",
    "JUBLFOOD": "Jubilant FoodWorks Ltd",
    "LICI": "Life Insurance Corporation of India",
    "LUPIN": "Lupin Ltd",
    "MARICO": "Marico Ltd",
    "MOTHERSON": "Samvardhana Motherson International Ltd",
    "MUTHOOTFIN": "Muthoot Finance Ltd",
    "NAUKRI": "Info Edge India Ltd",
    "NHPC": "NHPC Ltd",
    "NMDC": "NMDC Ltd",
    "OBEROIRLTY": "Oberoi Realty Ltd",
    "PAGEIND": "Page Industries Ltd",
    "PETRONET": "Petronet LNG Ltd",
    "PIDILITIND": "Pidilite Industries Ltd",
    "PNB": "Punjab National Bank",
    "PRESTIGE": "Prestige Estates Projects Ltd",
    "RECLTD": "REC Ltd",
    "SAIL": "Steel Authority of India Ltd",
    "SBICARD": "SBI Cards and Payment Services Ltd",
    "SIEMENS": "Siemens Ltd",
    "SRF": "SRF Ltd",
    "TATAPOWER": "Tata Power Company Ltd",
    "TORNTPHARM": "Torrent Pharmaceuticals Ltd",
    "TVSMOTOR": "TVS Motor Company Ltd",
    "UNIONBANK": "Union Bank of India",
    "VBL": "Varun Beverages Ltd",
    "VEDL": "Vedanta Ltd",
    "VOLTAS": "Voltas Ltd",
    "ZOMATO": "Zomato Ltd",
    "ZYDUSLIFE": "Zydus Lifesciences Ltd",
    "INTERGLOBE": "InterGlobe Aviation Ltd (IndiGo)",
    "PAYTM": "One97 Communications Ltd (Paytm)",
    "NYKAA": "FSN E-Commerce Ventures Ltd (Nykaa)",
    "POLICYBZR": "PB Fintech Ltd (PolicyBazaar)",
    "MRF": "MRF Ltd",
    "IRFC": "Indian Railway Finance Corporation Ltd",
    "RVNL": "Rail Vikas Nigam Ltd",
    "MAZAGON": "Mazagon Dock Shipbuilders Ltd",
}


def get_stock_name(symbol: str) -> str:
    """Get company name for a symbol."""
    # Remove exchange suffix
    base_symbol = symbol.replace(".NS", "").replace(".BO", "")
    return NSE_STOCK_NAMES.get(base_symbol, base_symbol)


def search_nse_stocks(query: str, limit: int = 20) -> list[dict]:
    """
    Search NSE stocks by symbol or company name.
    
    Args:
        query: Search query (symbol or company name)
        limit: Maximum results to return
        
    Returns:
        List of matching stocks with symbol and name
    """
    query_lower = query.lower()
    results = []
    
    all_symbols = set(NIFTY_50 + NIFTY_NEXT_50 + OTHER_NSE_STOCKS)
    
    for symbol in all_symbols:
        name = NSE_STOCK_NAMES.get(symbol, symbol)
        
        # Match by symbol or name
        if query_lower in symbol.lower() or query_lower in name.lower():
            results.append({
                "symbol": f"{symbol}.NS",
                "name": name,
                "match_type": "exact" if query_lower == symbol.lower() else "partial"
            })
    
    # Sort: exact matches first, then by symbol
    results.sort(key=lambda x: (x["match_type"] != "exact", x["symbol"]))
    
    return results[:limit]


# Export count
NSE_TOTAL_COUNT = len(set(NIFTY_50 + NIFTY_NEXT_50 + OTHER_NSE_STOCKS))
