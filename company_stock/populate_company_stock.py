import requests
import bs4 as bs
import os, django
from pandas_datareader import data as web
from pandas_datareader._utils import RemoteDataError
import datetime as dt
import numpy as np
# from django.core.management import settings
# settings.configure()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ml_demo.settings")
django.setup()
from ml_demo.settings import db_engine
from company_stock.models import CompanyDetails, CompanyStocks

def save_nifty_50_tickers():
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}
    resp = requests.get('https://en.wikipedia.org/wiki/NIFTY_50',
                        headers=headers)
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})

    for row in table.findAll('tr')[1:]:
        name = row.findAll('td')[0].text
        yahoo_sht = row.findAll('td')[1].text
        sector = row.findAll('td')[2].text
        #print name, yahoo_sht, sector
        c, created = CompanyDetails.objects.update_or_create(
            yahoo_sht=yahoo_sht,
            defaults={"name": name, "sector": sector}
        )
        if created:
            print "New Company details where added"


def get_data_from_yahoo():
    start = dt.datetime(2018, 1, 30)
    end = dt.datetime(2018, 1, 31)
    cmpy_details = CompanyDetails.objects.values_list('yahoo_sht', flat=True)
    print "cmpy_details : {}".format(cmpy_details[:10])
    for counter, ticker in enumerate(cmpy_details):
        try:
            # just in case your connection breaks, we'd like to save our progress!
            df = web.DataReader("{}.NS".format(ticker), "yahoo", start, end)
            df.replace(np.NAN, 0.0, inplace=True)
            df.reset_index(inplace=True,drop=False)

            df.rename(columns={'Open': 'open', 'High': 'high',
                               'Low': 'low', 'Close': 'close',
                               'Adj Close': 'adj_close', 'Volume': 'volume',
                               'Date': 'record_date'}, inplace=True)
            #print type(df)
            df['created_at'] = dt.datetime.now()
            df['updated_at'] = dt.datetime.now()
            df["ticker_id"] = ticker
            print len(df), counter * 1000
            df.insert(0, 'id', range(1 + (counter * 1000), len(df) + (counter * 1000) + 1))
            #print df.head()
            df.to_sql(CompanyStocks._meta.db_table, con=db_engine, if_exists='append', index=False)
        except RemoteDataError as e:
            print "Remote Data Error"
        #exit()

#get_data_from_yahoo()

