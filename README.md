分离式发交易

1. 解压 DIR 文件夹，里面为离线库。
   运行 pip3 install --no-index --find-links=DIR -r requirements.txt 安装库
   
1. 在联网电脑上，运行 python3 get_nonce.py, 获得nonce值和gas_price.

2. 运行python3 main2.py test.csv gas_limit gas_price nonce, 创建交易。
   
3. 在联网电脑上，运行 python3 sendex.py, 广播交易。
