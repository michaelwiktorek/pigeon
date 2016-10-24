import random

class Crypto:
    DH_LONG_SAFE_PRIME = 586157582832374913471571018240660200359557479705994709421351948303777042836505794894079281463273528928951213836364151063
    DH_BASE = 5
    
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

    def DH_private_key(self):
        self.DH_private_key = random.getrandbits(256)
        return self.DH_private_key

    def DH_public_key(self):
        self.DH_private_key()
        self.DH_public_key = pow(self.DH_BASE, self.DH_private_key, self.DH_LONG_SAFE_PRIME)
        return self.DH_public_key
        

if __name__ == "__main__":
    foo = Crypto()
    print foo.prob_safe_prime(random.getrandbits(2048))
    #print foo.DH_public_key()
