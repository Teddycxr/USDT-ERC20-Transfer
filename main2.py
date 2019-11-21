#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import csv
import os
import json
import binascii

from web3 import Web3

from config import *

EIP20_ABI = json.loads(
    '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')  # noqa: 501


def write_txn(file_name, sign_txn):
    TXN = os.path.join("Txn")
    if not os.path.exists(TXN):
        os.makedirs(TXN)

    f = open('Txn/' + file_name, 'w', encoding='utf8')
    # f.write(str(binascii.b2a_hex(sign_txn), encoding='utf-8'))
    f.write(sign_txn.hex())
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


def create_tx(nonce, address, amount, file_name):
    web3_off = Web3()

    contractaddress = Web3.toChecksumAddress(contract_address.lower())
    erc20 = web3_off.eth.contract(address=contractaddress, abi=EIP20_ABI)

    print("Current Nonce:{}".format(nonce))
    actual_amount = float(amount) * pow(10, dec)

    tx_address = Web3.toChecksumAddress(address.lower())
    txn_body = erc20.functions.transfer(tx_address, int(actual_amount)).buildTransaction(
        {'chainId': 1, 'gas': gas_limit, 'gasPrice': gas_price, 'nonce': nonce})

    print(txn_body)
    signed_txn_body = web3_off.eth.account.sign_transaction(txn_body, private_key=private_key)
    signed_tx = signed_txn_body.rawTransaction

    write_txn(file_name, signed_tx)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: ")
        print("python3 main_old.py [CSV_FILE_PATH] [gas_limit] [gas_price] [nonce]")
        print("Example: ")
        print("python3 main_old.py test.csv 60000 1584000000 93")
        exit(0)
    else:
        print("Start Creating TXs.")
        batch_list = CsvReader(sys.argv[1]).parse()

        gas_limit = int(sys.argv[2])
        gas_price = int(sys.argv[3])
        nonce = int(sys.argv[4])

        for i, tx in enumerate(batch_list):
            print("第{0}个地址: {1}, 金额： {2}".format(i + 1, tx[0], tx[1]))
            if i + 1 < 10:
                file_name = 'tx00{0}.txn'.format(i + 1)
            if i + 1 >= 10 and i + 1 < 100:
                file_name = 'tx0{0}.txn'.format(i + 1)
            if i + 1 >= 100:
                file_name = 'tx{0}.txn'.format(i + 1)

            create_tx(nonce, tx[0], tx[1], file_name)
            nonce += 1
        print("All TX Created.")
