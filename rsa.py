from crypto_util import Crypto_Util
import math
import sys

class RSA:
    PRIME_MIN_BYTES = 128
    
    def gen_keypair(self):
        p = Crypto_Util.rand_prob_prime(self.PRIME_MIN_BYTES)
        q = Crypto_Util.rand_prob_prime(self.PRIME_MIN_BYTES)
        n = p * q
        tot = n - (p + q -1)
        e = 65537
        # make sure e and tot are coprime
        while tot % e == 0:
            e = Crypto_Util.prob_prime(e + 1)
        d = Crypto_Util.mod_mult_inv(e, tot)
        self.public_mod = n
        self.public_exp = e
        self.private_exp = d
        return (n, e, d)

    def str_to_int(self, string):
        return int(string.encode('hex'), 16)

    def int_to_str(self, num):
        return hex(num)[2:][:-1].decode('hex')

    def encrypt(self, message, pub_key):
        mesg_num = self.str_to_int(message)
        n = pub_key[0]
        e = pub_key[1]
        return pow(mesg_num, e, n)

    def get_other_pub_key(self, pubkey):
        self.other_pub_key = pubkey
    
    def encrypt_known(self, message):
        return self.encrypt(message, self.other_pub_key)

    def decrypt(self, message):
        out_num = pow(message, self.private_exp, self.public_mod)
        # this because python adds '0x' and 'L' to the ends of the string
        out = self.int_to_str(out_num)
        return out

    def decipher_str(self, string):
        return self.decrypt(int(string))
    
    def encipher_str(self, string):
        return str(self.encrypt_known(string))

    def encipher_long_str(self, string):
        str_int = self.str_to_int(string)
        #num_chunks = float(self.bytes_needed(str_int))/(2 * self.PRIME_MIN_BYTES)
        num_chunks = float(sys.getsizeof(str_int))/sys.getsizeof(self.public_mod)
        # if message is small enough, just encrypt it
        # otherwise break it up
        if num_chunks < 1:
            return self.encipher_str(string)
        else:
            num_chunks = int(math.ceil(num_chunks))
            submessages = self.divide_str(string, num_chunks)
            subciphers = map(lambda x:self.encipher_str(x), submessages)
            return ":".join(subciphers)

    def decipher_long_str(self, string):
        subciphers = string.split(":")
        if len(subciphers) == 1:
            return self.decipher_str(subciphers[0])
        else:
            submessages = map(lambda x:self.decipher_str(x), subciphers)
            return "".join(submessages)

    def divide_str(self, string, chunks):
        chunk_size = len(string)/chunks
        return [string[i:i+chunk_size] for i in range(0, len(string), chunk_size)]
            

    def sign(self, message):
        print "TODO"

    def get_public_key(self):
        return (self.public_mod, self.public_exp)

    def get_private_key(self):
        print "TODO maybe don't need this"


if __name__ == "__main__":
    foo = RSA()
    foo.gen_keypair()
    foo_pubkey = foo.get_public_key()

    message = "the russians are coming"
    #print "message: " + message
    foo_cipher = foo.encrypt(message, foo_pubkey)
    #print "encrypted decimal: " + str(foo_cipher)
    foo_out = foo.decrypt(foo_cipher)
    #print "decrypted message: " + foo_out
    
