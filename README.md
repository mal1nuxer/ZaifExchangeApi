ZaifExchangeApi
======================
暗号通貨取引所Zaifで公開されているApiをPythonから扱えるようにしました。  
意図しない値が利用されることを想定していませんので公式ドキュメントを充分に参照してください。  
https://corp.zaif.jp/api-docs/

使い方
------

ZaifにてApiキーを取得してください。  
2016/08/21現在ではinfo, trade, withdrawの権限の有無を選択可能です。  
必要な権限がキーになくメソッドを利用した場合はエラーが表示されます。  
また現在のキーに設定されている権限はget_infoメソッドにより確認することが可能です。  

公開情報ApiにはApiキーは必要ありません。  
  
公開情報Apiのみの利用  
import Api_Zaif  
Zaif = Api_Zaif.Zaif()  
print(Zaif.last_price('btc_jpy'))  
  
取引Apiも利用する場合  
import Api_Zaif  
pub_key = 'str'  
sec_key = 'str'  
Zaif = Api_Zaif.Zaif(pub_key, sec_key)  
print(Zaif.get_info())  

留意
------
***
Pythonのネイティブモジュールで動くように作っていますが  
websocketを利用したws_depthについては別途モジュールが必要です  
https://github.com/liris/websocket-client  
こちらをご利用ください
***