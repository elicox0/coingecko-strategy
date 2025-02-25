import sqlite3

con = sqlite3.connect("coins.db")
cur = con.cursor()
cur.execute("CREATE TABLE market(id, symbol, name, image,\
                                 current_price, market_cap,\
                                 market_cap_rank, fully_diluted_valuation,\
                                 total_volume, high_24h, low_24h,\
                                 price_change_24h, price_change_percentage_24h,\
                                 circulating_supply, total_supply, max_supply,\
                                 ath, ath_change_percentage, ath_date, atl,\
                                 atl_change_percentage, atl_date, roi, last_updated)")

