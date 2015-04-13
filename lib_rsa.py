from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA512
import hashlib
from lib_user_input import force_integer_input
from lib_random import create_random_key
from lib_main_crypto import *
class rsa_keystore(object):
	# e = 65537 fixed
	def __init__(self):
		self.key_list = []
		self.key_fingerprint_list = []
		#self.key_type_list = []
	def generate_key(self):
		print("Generating 9984 bit RSA key")
		key = RSA.generate(9984)
		self.key_list.append(key)
		self.update_fingerprints()
	def update_fingerprints(self):
		self.key_fingerprint_list = []
		for i in range(0,len(self.key_list)):
			self.key_fingerprint_list.append(hashlib.sha256(bytes(str(self.key_list[i].n).encode())).hexdigest())
	def view_keys(self):
		if len(self.key_fingerprint_list) == 0:
			print("No keys found")
		else:
			for i in range(0,len(self.key_fingerprint_list)):
				print("Key number:",i+1)
				print("Fingerprint",self.key_fingerprint_list[i])
				# print("Size",self.key_list[i].size())
				print("Private key in possesion:", self.key_list[i].has_private())
	def export_key(self):
		kte = force_integer_input("Key to export:")-1
		try:
			kte_ac = self.key_list[kte]
			kte_n = kte_ac.n
			kte_str = str(kte_n)
			kte_hasprivate = kte_ac.has_private()
			if kte_hasprivate == True:
				export_priv = False
				epprompt = str(input("Export also your private key? [N]"))
				if epprompt == "Y" or epprompt == "y":
					export_priv = True
				if export_priv == True:
					kte_d = kte_ac.d
					kte_str = kte_str + "," + str(kte_d)
			encrypt_file_from_bytearray(bytearray(kte_str.encode()))
		except IndexError:
			print("Key not in keystore.")
	def import_key(self):
		keyraw, hmac_state, decryption_done = decrypt_file_to_bytearray()
		if hmac_state == False or decryption_done == False:
			print("Decryption Failed")
			return "F"
		else:
			keydec = (keyraw.decode()).split(",")
		if len(keydec) == 1:
			tuple_to_use = int(keydec[0]),65537
		elif len(keydec) == 2:
			tuple_to_use = int(keydec[0]),65537,int(keydec[1])
		self.key_list.append(RSA.construct(tuple_to_use))
		self.update_fingerprints()
	def delete_key(self):
		kte = force_integer_input("Key to delete:")-1
		self.key_list.pop(kte)
		self.update_fingerprints()
	def create_rsa_header(self):
		ktu = force_integer_input("Key to use:")-1
		try:
			ktu_ac = self.key_list[ktu]
			key_to_encrypt = create_random_key(1024)
			rsa_cipher = PKCS1_OAEP.new(ktu_ac,hashAlgo=SHA512)
			ciphered_key = rsa_cipher.encrypt(key_to_encrypt)
			decrypted_key = rsa_cipher.decrypt(ciphered_key)
			print(len(ciphered_key))
			header = bytearray()
			header.append(create_random_upper_half())
			header.extend(ciphered_key)
			header.extend(create_random_key(1823))
			return header, key_to_encrypt, True
		except IndexError:
			print("Key not in keystore")
			return False, False, False
	def decrypt_rsa_header(self, header):
		ktu = force_integer_input("Key to use:")-1
		try:
			ktu_ac = self.key_list[ktu]
			is_key_private = ktu_ac.has_private()
			if is_key_private == True:
				rsacipher = PKCS1_OAEP.new(ktu_ac,hashAlgo=SHA512)
				try:
					deciphered_header = rsacipher.decrypt(bytes(header[1:1249]))
					# print(deciphered_header)
					return deciphered_header, True
				except ValueError:
					print("Decryption Incorrect. Wrong key or tampered file.")
					return False, False
			else:
				print("The key selected doesn't have its private decryption exponent.")
		except IndexError:
			print("Key not in keystore")
			return False, False