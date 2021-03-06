"""
# Symmetric key encryption utilities

Follows "the Special Encryption" routine from Pass and Shelat
(Algorithm 157.2)
"""
from Crypto.Cipher import AES
from Crypto.Util import Counter
import os
import random


"""
## Problem 0.1: Generating Random Numbers in Python (5 points)

The following are three ways of generating random bytes in
Python. Which one is appropriate for cryptographic schemes (such
as shuffling the rows in your garbling table)? 

Use the internet and python documentation to research how
random, SystemRandom, and os.urandom work.

In a comment below this line, explain the differences between
each, and justify your choice of one of them.

TODO: Your answer goes here
"""
def random_bytes(n):
    # TODO: Your code goes here

    # Option 1
    # return os.urandom(n)

    # Option 2
    # return ''.join(chr(random.randint(0,256)) for _ in range(n))

    # Option 3
    # rnd = random.SystemRandom()
    # return ''.join(chr(rnd.randint(0,256)) for _ in range(n))

    return os.urandom(n)


KEYLENGTH = 128; # n from Course in Cryptography textbook

def generate_key():
    # this returns 16 bytes 
    return random_bytes(KEYLENGTH//8)


def lengthQuadruplingPRF(k, r):
    # Input: 16 byte key, 16 byte value
    # Output: 64 byte pseudorandom bytes
    assert len(k) == KEYLENGTH//8
    assert len(r) <= KEYLENGTH//8
    obj = AES.new(k, AES.MODE_CTR, counter=Counter.new(128))
    output = obj.encrypt(r*4)
    return output

"""
## Problem 0.2: Special Encryption (10 points)

From Pass and Shelat  (Course in Cryptography)
Implement the algorithm from the textbook. Use the provided 
`specialDecryption` function for clarification.
"""

def specialEncryption(k, m):
    # k: key, m: message 
    assert len(k) == KEYLENGTH//8
    assert len(m) <= KEYLENGTH//8 * 3  # m must be bounded in size

    # TODO: Your code goes here
    r = generate_key()
    prf = lengthQuadruplingPRF(k,r)
    # print("prf length",len(prf))

    # a&~a gives arbitrary length of zeros 
    n_zeros = b''.join( bytes([i&~i]) for (i,i) in zip( r, r ) )
    zeros_m = n_zeros + m 
    zeros_msg_xor_prf = b''.join( bytes([a^b]) for (a,b) in zip(zeros_m, prf))
    enc = r + zeros_msg_xor_prf
    return enc 


         
def specialDecryption(k, c):

    assert len(k) == KEYLENGTH//8
    assert len(c) > KEYLENGTH//8 * 2

    r = c[:KEYLENGTH//8]
    cip = c[KEYLENGTH//8:]

    # Compute the PRF
    prf = lengthQuadruplingPRF(k, r)

    # XORing the message
    # print("cip",cip,len(cip))
    # print("prf",prf,len(prf))
    assert len(cip) <= len(prf)
    msg = b''.join( bytes([a^b]) for (a,b) in zip( cip, prf ) )

    # Split into two
    pad = msg[:KEYLENGTH//8]
    m = msg[KEYLENGTH//8:]

    # Check the padding
    if pad != b'\x00'*(KEYLENGTH//8): return None
    return m


if __name__ == '__main__':
    # Test vectors for special encryption
    import random


    k = generate_key()
    for i in range(1000):
        l = random.randint(16,48)
        m = random_bytes(l)
        assert specialDecryption(k, specialEncryption(k, m)) == m
