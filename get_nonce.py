#!/usr/bin/python
# -*- coding: UTF-8 -*-
from web3 import Web3, HTTPProvider

from config import api_endpoint,source_addr

web3 = Web3(HTTPProvider(api_endpoint))

nonce = web3.eth.getTransactionCount(source_addr)
print('Nonce:', nonce)
gas_price = web3.eth.gasPrice
print('Gas_price', gas_price)

# 账户USDT 值
# erc20 = web3.eth.contract(address=contract_address, abi=EIP20_ABI)
# balance = erc20.functions.balanceOf(source_addr).call()
# print('USDT余额：',balance)
