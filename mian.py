#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import time
import csv
import os

from ethtoken.abi import EIP20_ABI
from web3 import Web3, HTTPProvider

from config import *

def record_log(addr, amount, txhash,file_name):
    LOG_DIR = os.path.join("Log")
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    f = open('Log/'+file_name,'a',encoding='utf8')
    f.writelines(addr+' '+str(amount/10**6)+' '+txhash+'\n')
    f.close()


class CsvReader(object):

    def __init__(self, csv_file):
        self.csv = csv_file

    def parse(self):
        result = []
        with open(self.csv, "r") as f:
            reader = csv.reader(f)
            for item in reader:
                result.append([item[0].strip(" "), item[1]])
        return result


class ContributeTokens(object):
    def __init__(self, api_endpoint, contract_address, private_key, source_addr):

        self.web3 = Web3(HTTPProvider(api_endpoint))

        contractaddress = self.web3.toChecksumAddress(contract_address.lower())
        self.erc20 = self.web3.eth.contract(address=contractaddress, abi=EIP20_ABI)
        self.private_key = private_key
        self.source_addr = source_addr
        self.nonce = -1.

        # print(self.web3.personal.importRawKey(private_key,'123456'))
        # print("")

    def wait_tx(self, addr, amount, txhash, times=1):
        # 以太坊15秒出一个块，每次尝试获取收据，如果没有成功等待15秒
        try:
            print("Address: %s recharge %d, start check at %d times, txhash: %s " % (addr, amount, times, txhash))

            receipt = self.web3.eth.getTransactionReceipt(txhash)
            status = receipt['status']
            if status == 1:
                record_log(addr, amount, txhash,'success_log.txt')
                print("Address:%s recharge %d Success, txhash: %s" % (addr, amount, txhash))
            else:
                record_log(addr, amount, receipt, 'failed_log.txt')
                print("Address:%s recharge %d Failed, txhash: %s" % (addr, amount, txhash))
        except Exception as e:
            print("Address: %s recharge check failed, txHash: %s, error is %s start check again " % (addr, txhash, e))
            time.sleep(15)
            times += 1
            self.wait_tx(addr, amount, txhash, times)

    def transfer(self, address, amount):
        """
        Function to transfer amount to the given address
        :param address:
        :param amount:
        :return:
        """
        name = self.erc20.functions.name().call()
        chainId = self.web3.eth.chainId
        print("erc20 Name:", name)
        # print("chainId: ", chainId)

        # Get Nonce first 交易流水号
        nonce = self.web3.eth.getTransactionCount(self.source_addr)
        print("Current Nonce:{}".format(nonce))
        # Update Nonce if needed
        if self.nonce < nonce:
            self.nonce = nonce
        else:
            # Probably in batch mode, need to auto add nonce.
            self.nonce += 1
            print("Fixed Nonce:{}".format(self.nonce))

        # Get Decimals
        # USDT 最小位数
        dec = self.erc20.functions.decimals().call()

        # 账户USDT 值
        balance = self.erc20.functions.balanceOf(self.source_addr).call()

        # gas_limit = self.web3.eth.estimateGas({'to': address, 'from': self.source_addr})
        gas_price = self.web3.eth.gasPrice  # gas_price = web3.toWei('2', 'gwei')
        print('gas_price: ', gas_price)
        actual_amount = amount * pow(10, dec)

        if actual_amount < balance:
            print("Enough Balance")

            txn_body = self.erc20.functions.transfer(address, int(actual_amount)).buildTransaction(
                {'gas': gas_limit, 'gasPrice': gas_price, 'nonce': self.nonce})

            print(txn_body)
            signed_txn_body = self.web3.eth.account.sign_transaction(txn_body, private_key=self.private_key)
            # output : signed_txn_body.rawTransaction  to file2

            txhash_bytes = self.web3.eth.sendRawTransaction(signed_txn_body.rawTransaction)
            txhash = self.web3.toHex(txhash_bytes)
            print('txhash: ', txhash)

            self.wait_tx(address, actual_amount, txhash)
        else:
            print('代币余额不足！')
            raise Exception("Not Enough Balance for transfer!")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ")
        print("python3 main_old.py [CSV_FILE_PATH]")
        print("Example: ")
        print("python3 main_old.py test.csv")
        exit(0)

    else:
        print("Start sending TXs.")
        batch_list = CsvReader(sys.argv[1]).parse()

        handler = ContributeTokens(api_endpoint=api_endpoint, contract_address=contract_address,
                                   private_key=private_key, source_addr=source_addr)
        for i, tx in enumerate(batch_list):
            print("第{0}个地址: {1}, 金额： {2}".format(i + 1, tx[0], tx[1]))
            tx_address = Web3.toChecksumAddress(tx[0].lower())
            handler.transfer(tx_address, float(tx[1]))
            print(tx_address)
        print("All TX Sent.")
