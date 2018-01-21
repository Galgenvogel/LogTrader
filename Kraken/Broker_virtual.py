'''
This is the Broker class.
The Broker connects with the Kraken account and does the trades

@author: mhansinger 

'''

import numpy as np
import pandas as pd
import krakenex
import time


class Broker_virtual(object):
    def __init__(self, input):
        self.__asset1 = input.asset1
        self.__asset2 = input.asset2
        self.__pair = input.asset1+input.asset2

        self.asset_status = False
        self.broker_status = False
        self.__k = krakenex.API()
        #self.__k.load_key('kraken.key')
        self.__balance_all = []
        self.__fee = input.fee
        self.__invest = input.investment
        self.__balance_df = []

        self.__column_names = []
        self.lastbuy = 0
        self.lastsell = 0

    def initialize(self):
        self.__column_names = ['Time stamp', self.__asset1, self.__asset2, self.__asset1+' shares', 'costs', self.__asset1+' price']
        self.__balance_df = pd.DataFrame([np.zeros(len(self.__column_names))], columns= self.__column_names)
        self.__balance_df['Time stamp'] = self.getTime()
        self.__balance_df[self.__asset2] = self.__invest
        self.__balance_df[self.__asset1+' price'] = self.asset_market_bid()

        print(self.__balance_df)

        # return self.__balance_df

    def buy_order(self):
        self.broker_status = True

        if self.asset_status is False:
            # this only for virtual
            try:
                __balance_np = np.array(self.__balance_df.tail())
            except AttributeError:
                print('Broker muss noch initialisiert werden!')

            __current_eur_funds = __balance_np[-1, 2] * 0.999999
            __current_costs = __current_eur_funds * self.__fee

            __asset_ask = self.asset_market_ask()

            __new_shares = (__current_eur_funds - __current_costs) / __asset_ask
            __new_XETH = __new_shares * __asset_ask
            __new_eur_fund = __balance_np[-1, 2] - __current_eur_funds  # --> sollte gegen null gehen

            # update time
            __time = self.getTime()

            __balance_update_vec = [[__time, __new_XETH, __new_eur_fund, __new_shares, __current_costs, __asset_ask ]]
            __balance_update_df = pd.DataFrame(__balance_update_vec, columns=self.__column_names)
            self.__balance_df = self.__balance_df.append(__balance_update_df)

            # write as csv file
            self.writeCSV(self.__balance_df)
            print(' ')
            print(__balance_update_df)
            print(' ')

            self.lastbuy=__asset_ask

            self.asset_status = True

        else:
            print('Hast kein Geld zum Kaufen')

        self.broker_status = False


    # Bug to fix
    def sell_order(self):
        self.broker_status = True
        __asset_bid = self.asset_market_bid()

        if self.asset_status is True:
            # this only for virtual
            try:
                __balance_np = np.array(self.__balance_df.tail())
            except AttributeError:
                print('Broker muss noch initialisiert werden!')

            __asset_bid = self.asset_market_bid()
            __current_shares = __balance_np[-1, 3] * 0.999999
            __current_costs = __current_shares * __asset_bid * self.__fee

            __new_eur_fund = __current_shares * __asset_bid - __current_costs

            __new_shares = __balance_np[-1, 3] - __current_shares  # --> sollte gegen null gehen
            __new_XETH = __new_shares * __asset_bid

            # update time
            __time = self.getTime()

            __balance_update_vec = [[__time, __new_XETH, __new_eur_fund, __new_shares, __current_costs, __asset_bid]]
            __balance_update_df = pd.DataFrame(__balance_update_vec, columns=self.__column_names)
            self.__balance_df = self.__balance_df.append(__balance_update_df)

            # write as csv file
            self.writeCSV(self.__balance_df)
            print(__balance_update_df)
            print(' ')

            self.lastsell = __asset_bid
            self.asset_status = False

        else:
            print('Hast nix zu verkaufen')

        self.broker_status = False


    def idle(self):
        self.broker_status = True
        try:
            __balance_np = np.array(self.__balance_df.tail())
        except AttributeError:
            print('Broker muss noch initialisiert werden!')
        #
        if self.asset_status is True:
            __market_price = self.asset_market_ask()
        elif self.asset_status is False:
            __market_price = self.asset_market_bid()
        #
        __new_shares = __balance_np[-1,3]
        __new_assets = __new_shares*__market_price
        __new_eur_fund = __balance_np[-1,2]
        __current_costs = 0
        #
        # update time
        __time = self.getTime()
        #
        # alter status ist wie neuer balance vektor
        __balance_update_vec = [[__time, __new_assets, __new_eur_fund, __new_shares, __current_costs, __market_price]]
        __balance_update_df = pd.DataFrame(__balance_update_vec, columns=self.__column_names)
        self.__balance_df = self.__balance_df.append(__balance_update_df)

        # write as csv file
        self.writeCSV(self.__balance_df)

       # print(__balance_update_df)
       # print(' ')

        self.broker_status = False


    def virtual_balance(self):
        print(self.__balance_df.tail())

    def get_broker_status(self):
        return self.broker_status

    def asset_balance(self):
        self.__balance_all = self.__k.query_private('Balance')
        balance_str = self.__balance_all['result'][self.__asset1]
        balance = float(balance_str)
        print(balance)

    def asset_market_bid(self):
        __market_bid = self.__k.query_public('Ticker', {'pair': self.__pair})['result'][self.__pair]['b']
        return float(__market_bid[0])

    def asset_market_ask(self):
        __market_ask = self.__k.query_public('Ticker', {'pair': self.__pair})['result'][self.__pair]['a']
        return float(__market_ask[0])

    def market_price(self):
        __market = self.__k.query_public('Ticker', {'pair': self.__pair})['result'][self.__pair]['c']
        return float(__market[0])

    def get_eur_funds(self):
        __eur_funds = self.__k.query_private('Balance')['result'][self.__asset2] # muss noch allgemein angepasst werden!
        return float(__eur_funds)

    def get_asset_funds(self):
        __asset_funds = self.__k.query_private('Balance')['result'][self.__asset1]
        return float(__asset_funds)

    def getTime(self):
        #return int(time.time())
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    def writeCSV(self,__df):
        __filename = self.__pair+'_balance.csv'
        pd.DataFrame.to_csv(__df,__filename)





