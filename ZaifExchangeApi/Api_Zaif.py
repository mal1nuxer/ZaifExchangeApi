# -*- coding: utf-8 -*-
import urllib
import json
import time
import hmac
import hashlib
import httplib

publicMethodList = ('last_price', 'ticker', 'trades', 'depth')
tradeMethodList = ('get_info', 'trade_history', 'active_orders', 'trade',
                   'cancel_order', 'withdraw', 'deposit_history',
                   'withdraw_history')


class Zaif(object):
    def __init__(self, api_key=None, api_secret=None):
        self.__api_key = str(api_key) if api_key is not None else ''
        self.__api_secret = str(api_secret) if api_secret is not None else ''
        self.__public_set = publicMethodList
        self.__trade_set = tradeMethodList

    def __api_query(self, method, options=None):
        if not options:
            options = {}
        base_url = 'https://api.zaif.jp/'

        if method in self.__public_set:
            request_url = base_url + 'api/1/' + method + '/' + options
            response = json.loads(urllib.urlopen(request_url).read())
            return response

        elif method in self.__trade_set:
            nonce = time.time()
            zaif_query = {"nonce": str(nonce), "method": method}

            if not options == {}:
                zaif_query.update(options)

            headers = {"key": self.__api_key,
                       "sign": hmac.new(self.__api_secret,
                                        urllib.urlencode(zaif_query),
                                        digestmod=hashlib.sha512).hexdigest()}
            session = httplib.HTTPSConnection("zaif.jp")
            session.request("post", "/tapi", urllib.urlencode(zaif_query),
                            headers)
            response = json.loads(session.getresponse().read())
            session.close()

            if response['success'] == 1:
                return response

            elif response['success'] == 0:
                print(response)

    # PublicAPI

    def last_price(self, currency_pair):
        """終値を得る"""
        return self.__api_query('last_price', currency_pair)

    def ticker(self, currency_pair):
        """ティッカー"""
        return self.__api_query('ticker', currency_pair)

    def public_trade_history(self, currency_pair):
        """公開されている全ての取引履歴"""
        return self.__api_query('trades', currency_pair)

    def depth(self, currency_pair):
        """板情報"""
        return self.__api_query('depth', currency_pair)

    # TradeAPI

    def get_info(self):
        """
        現在の余力および残高、APIの権限、トレード数、
        アクティブ注文数、タイムスタンプを取得します
        """
        return self.__api_query('get_info')

    def your_trade_history(self, **options):
        """
        ユーザーの取引履歴取得
        オプション名    (必須, 説明, 型, 初期値)
        from_rec      (No, この順番のレコードから取得, 数値, 0)
        count         (No, 取得するレコード数, 数値, 1000)
        from_id       (No, このトランザクションIDのレコードから取得, 数値, 0)
        end_id        (No, このトランザクションIDのレコードまで取得, 数値, 無限)
        order         (No, ソート順, ASC (昇順)もしくは DESC (降順), DESC)
        since         (No, 開始タイムスタンプ, UNIX time, 0)
        end           (No, 終了タイムスタンプ, UNIX time, 無限)
        currency_pair (No, 通貨ペア。指定なしで全ての通貨ペア, (例) btc_jpy, 全ペア)
        """
        try:
            if options['from_rec']:
                options['from'] = options.pop('from_rec')
        except KeyError:
            pass
        return self.__api_query('trade_history', options)

    def active_orders(self, currency_pair=None):
        """
        現在有効な注文一覧
        オプション名    (必須, 説明, 型, 初期値)
        currency_pair (No, 通貨ペア。指定なしで全ての通貨ペア, (例) btc_jpy, 全ペア)
        """
        query = {}
        if currency_pair is not None:
            query['currency_pair'] = currency_pair
        return self.__api_query('active_orders', query)

    def trade(self, currency_pair, action, price, amount, limit=None):
        """
        注文を行う
        オプション名      (必須, 説明, 型)
        currency_pair	(Yes, 発注する通貨ペア, (例) btc_jpy)
        action	        (Yes, 注文の種類, bid もしくは ask)
        price	        (Yes, 指値注文価格, 数値)
        amount	        (Yes, 数量(例: 0.3), 数値)
        limit	        (No,  (リミット注文価格, 数値)
        """
        query = {'currency_pair': currency_pair,
                 'action': action,
                 'price': price,
                 'amount': amount}
        if limit is not None:
            query['limit'] = limit
        return self.__api_query('trade', query)

    def cancel_order(self, order_id):
        """
        注文の取り消し
        オプション名   (必須, 説明, 型)
        order_id     (Yes, 注文ID(tradeまたはactive_ordersで取得), 数値)
        """
        query = {'order_id': order_id}
        return self.__api_query('cancel_order', query)

    def withdraw(self, currency, address, amount, opt_fee=None):
        """
        暗号通貨の引き出しリクエスト
        オプション名  (必須, 説明, 型)
        currency	(Yes, 引き出す通貨	, btc / mona)
        address	    (Yes, 送信先のアドレス, 文字列)
        amount	    (Yes, 引き出す金額(例: 0.3), 数値)
        opt_fee	    (No,  採掘者への手数料(例: 0.003), 数値)
        """
        query = {'currency': currency,
                 'address': address,
                 'amount': amount}
        if opt_fee is not None:
            query['opt_fee'] = opt_fee
        return self.__api_query('withdraw', query)

    def deposit_history(self, currency, **options):
        """
        入金履歴の取得
        オプション名    (必須, 説明, 型, 初期値)
        currency      (Yes, jpy/btc/mona, 文字列, None)
        from          (No, この順番のレコードから取得, 数値, 0)
        count         (No, 取得するレコード数, 数値, 1000)
        from_id       (No, この入金IDのレコードから取得, 数値, 0)
        end_id        (No, この入金IDのレコードまで取得, 数値, 無限)
        order         (No, ソート順, ASC (昇順)もしくは DESC (降順), DESC)
        since         (No, 開始タイムスタンプ, UNIX time, 0)
        end           (No, 終了タイムスタンプ, UNIX time, 無限)
        """
        query = {'currency': currency}
        if not options == {}:
            query.update(options)
        return self.__api_query('deposit_history', query)

    def withdraw_history(self, currency, **options):
        """
        出金履歴の取得
        オプション名    (必須, 説明, 型, 初期値)
        currency      (Yes, jpy/btc/mona, TEXT)
        from          (No, この順番のレコードから取得, 数値, 0)
        count         (No, 取得するレコード数, 数値, 1000)
        from_id       (No, この出金IDのレコードから取得, 数値, 0)
        end_id        (No, この出金IDのレコードまで取得, 数値, 無限)
        order         (No, ソート順, ASC (昇順)もしくは DESC (降順), DESC)
        since         (No, 開始タイムスタンプ, UNIX time, 0)
        end           (No, 終了タイムスタンプ, UNIX time, 無限)
        """
        query = {'currency': currency}
        if not options == {}:
            query.update(options)
        return self.__api_query('withdraw_history', query)

    # StreamingApi

    def ws_depth(self, currency_pair):
        """
        websocket-clientモジュールが必要です
        https://github.com/liris/websocket-client
        確立されたコネクションを返しますので
        json.loads([return先].recv())をする毎に板情報を受け取れます
        """
        import websocket
        ws = 'ws://api.zaif.jp:8888/stream?currency_pair=%s' % currency_pair
        return websocket.create_connection(ws)
