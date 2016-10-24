import random
import os

class Diffie:
    DH_PRIME_3072 = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AAAC42DAD33170D04507A33A85521ABDF1CBA64ECFB850458DBEF0A8AEA71575D060C7DB3970F85A6E1E4C7ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261AD2EE6BF12FFA06D98A0864D87602733EC86A64521F2B18177B200CBBE117577A615D6C770988C0BAD946E208E24FA074E5AB3143DB5BFCE0FD108E4B82D120A93AD2CAFFFFFFFFFFFFFFFF
    
    DH_LONG_SAFE_PRIME = 586157582832374913471571018240660200359557479705994709421351948303777042836505794894079281463273528928951213836364151063
    DH_BASE = 2

    PRIV_LEN_BYTES = 128
    
    def prob_safe_prime(self, start):
        s = start
        # guarantee that s is odd
        if s % 2 == 0:
            s += 1
        while True:
            if self.miller_rabin_test(s) and self.miller_rabin_test((s-1)/2):
                return s
            else:
                s += 2

    def miller_rabin_test(self, num):
        bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
        prime = True
        for base in bases:
            prime = prime and (pow(base, num-1, num) == 1)
            if not prime:
                return prime
        return prime

    def private_key(self):
        # This is where our security comes from
        # Number of bytes we can send scales with PRIV_LEN_BYTES 
        num = int(os.urandom(self.PRIV_LEN_BYTES).encode('hex'), 16)
        self.DH_private_key = num
        return self.DH_private_key

    def public_key(self):
        self.DH_private_key()
        self.DH_public_key = pow(self.DH_BASE, self.DH_private_key, self.DH_PRIME_3072)
        return self.DH_public_key

    def shared_secret(self, other_pub_key):
        self.shared_secret = pow(other_pub_key, self.DH_private_key, self.DH_PRIME_3072)
        return self.shared_secret
        

if __name__ == "__main__":
    foo = Diffie()
    bar = Diffie()
    #print foo.prob_safe_prime(random.getrandbits(2048))
    A = foo.public_key()
    B = bar.public_key()
    print foo.shared_secret(B) == bar.shared_secret(A)
