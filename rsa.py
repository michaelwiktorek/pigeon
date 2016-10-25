from crypto_util import Crypto_Util

class RSA:
    def gen_keypair(self):
        p = Crypto_Util.rand_prob_prime(128)
        q = Crypto_Util.rand_prob_prime(128)
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

    def encrypt(self, message, pub_key):
        mesg_num = int(message.encode('hex'), 16)
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
        out = hex(out_num)[2:][:-1].decode('hex')
        return out

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
    print "message: " + message
    foo_cipher = foo.encrypt(message, foo_pubkey)
    print "encrypted decimal: " + str(foo_cipher)
    foo_out = foo.decrypt(foo_cipher)
    print "decrypted message: " + foo_out
    
