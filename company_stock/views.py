from django.shortcuts import render
import traceback
from company_stock.models import CompanyStocks
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
#import pylab as plt
from django.http import HttpResponse
from io import BytesIO
import base64
from matplotlib import style
from matplotlib.finance import candlestick_ohlc
from matplotlib import dates as mdates
from datetime import datetime, timedelta
import numpy as np
from collections import Counter
from sklearn import neighbors, svm
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split

def closegraph(ticker='ADANIPORTS', start_date=None, end_date=None):
    qs = CompanyStocks.objects.select_related().filter(
            ticker__yahoo_sht=ticker
    )
    if start_date and end_date:
        qs = qs.filter(created_at__range=(start_date, end_date))
    q = qs.values('adj_close', 'record_date', 'volume')
    df = pd.DataFrame.from_records(q)
    #print df.head()
    #df['100ma'] = df['adj_close'].rolling(window=100, min_periods=0).mean()
    #print df.head()
    style.use('ggplot')
    f = plt.figure(figsize=(10, 7))
    ax1 = plt.subplot2grid((10, 7), (0, 0), rowspan=7, colspan=7)
    ax2 = plt.subplot2grid((10, 7), (8, 0), rowspan=2, colspan=7, sharex=ax1)

    #ax1.plot(df["100ma"])
    ax1.plot(df["adj_close"], label='Adj Close', color='b')
    ax1.legend()
    ax2.plot(df["volume"], label='Volume', color='g')
    ax2.legend()

    figfile = BytesIO()
    plt.savefig(figfile, format='png' ,bbox_inches='tight')
    figfile.seek(0)  # rewind to beginning of file
    figdata_png = base64.b64encode(figfile.getvalue())
    return figdata_png


def generate_ohlc_graph(ticker='ADANIPORTS', start_date=None, end_date=None):
    style.use('ggplot')
    qs = CompanyStocks.objects.filter(
            ticker__yahoo_sht=ticker
    )
    if start_date and end_date:
        qs = qs.filter(created_at__range=(start_date, end_date))
    q = qs.only('adj_close', 'record_date', 'volume', 'high', 'low', 'open').extra(
            {'adj_close': "CAST(adj_close as FLOAT)",
                  'volume': "CAST(volume as FLOAT)",
                  'high': "CAST(high as FLOAT)",
                  'low': "CAST(low as FLOAT)",
                  'open': "CAST(open as FLOAT)"})
    df = pd.DataFrame.from_records([rec.__dict__ for rec in q])
    df['record_date'] = pd.to_datetime(df['record_date'])
    df.set_index(['record_date'], inplace=True)
    df.info()
    df_ohlc = df['adj_close'].resample('10D').ohlc()
    df_volume = df['volume'].resample('10D').sum()


    df_ohlc.reset_index(inplace=True)
    df_ohlc['record_date'] = df_ohlc['record_date'].map(mdates.date2num)
    #print df.head()
    fig = plt.figure(figsize=(7, 7))
    ax1 = plt.subplot2grid((10, 7), (0, 0), rowspan=6, colspan=7)
    ax2 = plt.subplot2grid((10, 7), (7, 0), rowspan=3, colspan=7)
    ax1.xaxis_date()
    #print df_ohlc.values[:4]

    candlestick_ohlc(ax1, df_ohlc.values, width=5, colorup='g')
    ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)
    figfile = BytesIO()
    plt.savefig(figfile, format='png', bbox_inches='tight')
    figfile.seek(0)  # rewind to beginning of file
    figdata_png = base64.b64encode(figfile.getvalue())
    return figdata_png


def process_data_for_labels(ticker, start_date=None, end_date=None):
    hm_days = 7
    qs = CompanyStocks.objects.filter(
        ticker__yahoo_sht=ticker
    ).filter(
        adj_close__gt=0
    )
    if start_date and end_date:
        qs = qs.filter(record_date__range=(start_date, end_date))
    qs = qs.only('adj_close', 'record_date').extra({'adj_close': "CAST(adj_close as FLOAT)"}).order_by('-record_date')
    #print qs
    df = pd.DataFrame.from_records([q.__dict__ for q in qs])
    #print df.info()
    df.rename(columns={'adj_close': ticker}, inplace=True)
    #df.loc[(df!=0.0).any(axis=1)]
    #print df.head()
    #print df[ticker][:2], df[ticker][:2].shift(-1)
    #exit()
    tickers = df.columns.values.tolist()
    #df.fillna(0, inplace=True)
    #new_df = pd.DataFrame()
    for i in range(1, hm_days+1):
        df['{}_{}d'.format(ticker,i)] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]

    #df.fillna(0, inplace=True)
    #print df.head()
    return tickers, df


def buy_sell_hold(*args):
    cols = [c for c in args]
    requirement = 0.02
    for col in cols:
        if col > requirement:
            return 1
        if col < -requirement:
            return -1
    return 0


def extract_featuresets(ticker, start_date=None, end_date=None):
    tickers, df = process_data_for_labels(ticker, start_date, end_date)
    #print df.head()
    #exit()

    df['{}_target'.format(ticker)] = list(map(buy_sell_hold,
                                               df['{}_1d'.format(ticker)],
                                               df['{}_2d'.format(ticker)],
                                               df['{}_3d'.format(ticker)],
                                               df['{}_4d'.format(ticker)],
                                               df['{}_5d'.format(ticker)],
                                               df['{}_6d'.format(ticker)],
                                               df['{}_7d'.format(ticker)] ))
    #print df['{}_target'.format(ticker)]
    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('Data spread:',Counter(str_vals))

    df_vals = df[ticker].pct_change()
    df.fillna(0, inplace=True)
    df = df.replace([np.inf, -np.inf], 0)
    #df.dropna(inplace=True)
    #df_vals = df[[tick for tick in tickers]].pct_change()
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)
    X = df_vals.values
    y = df['{}_target'.format(ticker)].values

    return X,y,df

def do_ml(ticker, start_date=None, end_date=None):
    X, y, df = extract_featuresets(ticker, start_date, end_date)

    X_train, X_test, y_train,  y_test = train_test_split(X, y, test_size=0.25)
    clf = VotingClassifier([('lsvc', svm.LinearSVC()),
                            ('knn', neighbors.KNeighborsClassifier()),
                            ('rfor', RandomForestClassifier())])
    #print X_train.shape, y_train.shape
    #print "++++++++++++++++++"
    X_train = X_train.reshape(-1, 1)
    y_train = y_train.reshape(-1, 1)
    #print X_train.shape, y_train.shape
    clf.fit(X_train, y_train)
    X_test = X_test.reshape(-1, 1)
    y_test = y_test.reshape(-1, 1)
    confidence = clf.score(X_test, y_test)
    #print 'accuracy:{}'.format(confidence)

    predictions = clf.predict(X_test)
    #print'Predicted class counts: ', Counter(predictions)
    #print''
    #print''
    return confidence, predictions

def index(request):
    """Handle all request types and return response as per DB url, method/platform/org_id
    Args:
        request: Request Object
        url: requested url path, without base url
    """
    ticker_graph = ''
    ohlc_graph = ''
    confidence = 'NA'
    predictions = {1: 'NA', -1: 'NA', 0: 'NA'}
    try:
        current_time = datetime.now()
        start_date = (current_time - timedelta(days=10)).strftime('%Y-%m-%d')
        end_date = current_time.strftime('%Y-%m-%d')
        #ticker_graph = closegraph('ADANIPORTS', start_date, end_date)
        #ohlc_graph = generate_ohlc_graph(ticker='ADANIPORTS')
        start_date = (current_time - timedelta(days=9)).strftime('%Y-%m-%d')
        #process_data_for_labels('ADANIPORTS', start_date, end_date)
        confidence, predictions = do_ml('ADANIPORTS', start_date=None, end_date=None)
        predictions =  dict(Counter(predictions))
    except Exception:
        print traceback.format_exc()

    return render(request, 'index.html', {
            'ticker_graph': ticker_graph.decode('utf8'),
            'ohlc_graph': ohlc_graph.decode('utf-8'),
            'confidence': confidence,
            'predictions': predictions
        })
