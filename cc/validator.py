from pycoin.encoding import a2b_hashed_base58, EncodingError


def validate(address, magic_bytes):
	try:
		return a2b_hashed_base58(address)[:1] in bytes(map(int, magic_bytes.split(',')))
	except EncodingError:
		return False
