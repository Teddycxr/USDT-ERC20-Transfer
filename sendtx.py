#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import os
import binascii

from web3 import Web3, HTTPProvider

from config import api_endpoint

web3 = Web3(HTTPProvider(api_endpoint))


def record_log(txhash, file_name):
    LOG_DIR = os.path.join("Log")
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    f = open('Log/' + file_name, 'a', encoding='utf8')
    f.writelines(txhash + '\n')
    f.close()


def wait_tx(txhash, times=1):
    # 以太坊15秒出一个块，每次尝试获取收据，如果没有成功等待15秒
    try:
        print("start check at %d times, txhash: %s " % (times, txhash))

        receipt = web3.eth.getTransactionReceipt(txhash)
        status = receipt['status']
        if status == 1:
            record_log(txhash, 'success_log.txt')
            print("Success, txhash: %s" % (txhash))
        else:
            record_log(receipt, 'failed_log.txt')
            print("Failed, txhash: %s" % (txhash))
    except Exception as e:
        print("check failed, txHash: %s, error is %s start check again " % (txhash, e))
        time.sleep(15)
        times += 1
        wait_tx(txhash, times)


def send_tx():
    file_list = []
    result = os.popen("ls Txn/")
    res = result.read()
    for line in res.splitlines():
        if '.' not in line:
            res2 = os.popen("ls Txn/" + line)
            for j in res2.read().splitlines():
                file_list.append(line + "/" + j)
        else:
            file_list.append(line)

    for i in file_list:
        f = open('Txn/' + i, 'r', encoding='utf8')
        signed_txn = f.read()
        f.close()

        # data = binascii.a2b_hex(signed_txn)
        data = bytes.fromhex(signed_txn[2:])

        txhash_bytes = web3.eth.sendRawTransaction(data)
        txhash = web3.toHex(txhash_bytes)
        print('txhash: ', txhash)

        wait_tx(txhash)


if __name__ == '__main__':
    send_tx()
