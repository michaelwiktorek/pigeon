import os

# Helpful cryptographic utilities
class Crypto_Util:
    @staticmethod
    def rand_bytes(length_bytes):
        return int(os.urandom(length_bytes).encode('hex'), 16)

    @staticmethod
    def prob_safe_prime(start):
        s = start
        # guarantee that s is odd
        if s % 2 == 0:
            s += 1
        while True:
            if Crypto_Util.miller_rabin_test(s) and Crypto_Util.miller_rabin_test((s-1)/2):
                return s
            else:
                s += 2

    @staticmethod
    def prob_prime(start):
        s = start
        # guarantee that s is odd
        if s % 2 == 0:
            s += 1
        while True:
            if Crypto_Util.miller_rabin_test(s):
                return s
            else:
                s += 2
          
    @staticmethod
    def miller_rabin_test(num):
        bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
        prime = True
        for base in bases:
            prime = prime and (pow(base, num-1, num) == 1)
            if not prime:
                return prime
        return prime

if __name__ == "__main__":
    print Crypto_Util.prob_safe_prime(Crypto_Util.rand_bytes(32))
