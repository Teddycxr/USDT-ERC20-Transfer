分离式发交易

1. 在联网电脑上，运行 python3 get_nonce.py, 获得nonce值和gas_price.

2. 把nonce和gas_price填入config.py.
   运行python3 main2.py test.csv, 创建交易。
   
3. 在联网电脑上，运行 python3 sendex.py, 广播交易。
