from breeze_connect import BreezeConnect
import inspect

print("get_option_chain_quotes")
print(inspect.signature(BreezeConnect.get_option_chain_quotes))

print("\nget_contract_name")
print(inspect.signature(BreezeConnect.get_contract_name))

print("\nget_names")
print(inspect.signature(BreezeConnect.get_names))

print("\nget_quotes")
print(inspect.signature(BreezeConnect.get_quotes))