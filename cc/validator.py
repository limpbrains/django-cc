from pycoin.encoding import is_valid_bitcoin_address

def validate(address, magic_bytes):
	return is_valid_bitcoin_address(address, bytes(map(int, magic_bytes.split(','))))
