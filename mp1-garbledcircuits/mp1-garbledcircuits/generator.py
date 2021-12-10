"""
# Problem 2: Garbled Circuit Generator (20 points)
"""

import circuit
from circuit import BooleanCircuit
import json
from util import specialDecryption, specialEncryption, generate_key
import os
import random

"""
## Problem 2.01: implement a random shuffling routine (5 points)
Hint: use knuth-fischer-yates shuffling

    Use util.random_bytes for randomness.

    http://www.i-programmer.info/programming/theory/2744-how-not-to-shuffle-the-kunth-fisher-yates-algorithm.html

    Note: random.shuffle() from python stdlib does not count!
"""
def shuffle(a):
    assert type(a) is list
    # TODO: sort a in place, and return None
    def swap(lst,foo,bar):
        # print()
        # print(lst[foo],lst[bar])
        tmp = lst[foo]
        lst[foo] = lst[bar]
        lst[bar] = tmp
        # print(lst[foo],lst[bar])
        return None

    n = len(a)
    for i in range(n):
        swap(a,i,random.randint(i,n - 1))
    return None



"""
## Problem 2: Garbled Circuit Generator (15 points)
"""

class GarbledCircuitGenerator(BooleanCircuit):
    def __init__(self, from_json=None):
        # The superclass constructor initializes the gates and topological sorting
        super(GarbledCircuitGenerator,self).__init__(from_json=from_json)

    def garble(self):
        
        # Generate new wire labels
        self.wire_labels = {} # maps wire id to {"0":label0 ,"1": label1}

        # TODO: your code goes here
        print("Generate new wire labels")
        for i in ["w1","w2","w3","w4","w5","w6","w7"]:
            self.wire_labels[i] = [generate_key().hex(),generate_key().hex()]
        print(self.wire_labels)

        # Generate garble tables

        # TODO: your code goes here
        self.garble_table = {}
        print()
        print("Generating Garbled Tables")
        
        # g1 AND
        self.garble_table["g1"] = [specialEncryption(\
                bytes.fromhex(self.wire_labels["w1"][0]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w2"][0]),\
                bytes.fromhex(self.wire_labels["w5"][0]))).hex(),\
                    \
                specialEncryption(bytes.fromhex(self.wire_labels["w1"][0]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w2"][1]),\
                bytes.fromhex(self.wire_labels["w5"][0]))).hex(),\
                    \
                specialEncryption(bytes.fromhex(self.wire_labels["w1"][1]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w2"][0]),\
                bytes.fromhex(self.wire_labels["w5"][0]))).hex(),\
                    \
                specialEncryption(bytes.fromhex(self.wire_labels["w1"][1]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w2"][1]),\
                bytes.fromhex(self.wire_labels["w5"][1]))).hex()\
                    \
                ]
        shuffle(self.garble_table["g1"])
        print(self.garble_table["g1"])
        # gates[gid]["garble_table"] = self.garble_table[gid]

        #g2 XOR
        self.garble_table["g2"] = [specialEncryption(\
                bytes.fromhex(self.wire_labels["w3"][0]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w4"][0]),\
                bytes.fromhex(self.wire_labels["w6"][1]))).hex(),\
                    \
                specialEncryption(bytes.fromhex(self.wire_labels["w3"][0]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w4"][1]),\
                bytes.fromhex(self.wire_labels["w6"][1]))).hex(),\
                    \
                specialEncryption(bytes.fromhex(self.wire_labels["w3"][1]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w4"][0]),\
                bytes.fromhex(self.wire_labels["w6"][1]))).hex(),\
                    \
                specialEncryption(bytes.fromhex(self.wire_labels["w3"][1]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w4"][1]),\
                bytes.fromhex(self.wire_labels["w6"][0]))).hex()\
                    \
                ]
        shuffle(self.garble_table["g2"])
        print(self.garble_table["g2"])

        #g3 XOR
        self.garble_table["g3"] = [specialEncryption(\
                bytes.fromhex(self.wire_labels["w5"][0]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w6"][0]),\
                bytes.fromhex(self.wire_labels["w7"][1]))).hex(),\
                    \
                specialEncryption(bytes.fromhex(self.wire_labels["w5"][0]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w6"][1]),\
                bytes.fromhex(self.wire_labels["w7"][1]))).hex(),\
                    \
                specialEncryption(bytes.fromhex(self.wire_labels["w5"][1]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w6"][0]),\
                bytes.fromhex(self.wire_labels["w7"][1]))).hex(),\
                    \
                specialEncryption(bytes.fromhex(self.wire_labels["w5"][1]),\
                specialEncryption(bytes.fromhex(self.wire_labels["w6"][1]),\
                bytes.fromhex(self.wire_labels["w6"][0]))).hex()\
                    \
                ]

        shuffle(self.garble_table["g3"])
        print(self.garble_table["g3"])
        

        
    def output(self, outfile, inputs=None, debug=True):
        # Save as a JSON file, with wire lables for debugging
        obj = {}
        gates = {}
        for gid,gate in self.gates.items():
            gates[gid] = gate.copy() # Copy the gate object directly
            gates[gid]["garble_table"] = self.garble_table[gid]
        obj["gates"] = gates

        # Output wire labels in debug mode
        if debug: 
            obj["wire_labels"] = self.wire_labels

        if inputs is not None:
            print('Input available')
            assert len(inputs) == len(self.input_wires)
            input_labels = {}
            for wid,v in inputs.items():
                assert v in (0,1)
                input_labels[wid] = self.wire_labels[wid][v]
                obj["inputs"] = input_labels

        with open(outfile,"w") as f:
            json.dump(obj, f, indent=4)
        print('Wrote garbled circuit', outfile)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("usage: python generator.py <circuit.json> <outfile.json>")
        sys.exit(1)

    filename = sys.argv[1]
    obj = json.load(open(filename))


    # Circuit
    c = GarbledCircuitGenerator(from_json=obj)
    print('Circuit loaded: %d gates, %d input wires, %d output_wires, %d total' \
        % (len(c.gates), len(c.input_wires), len(c.output_wires), len(c.wires)))
    
    # Generate the circuit
    c.garble()

    # Load the inputs
    inputs = obj["inputs"]

    # Write the output
    outfile = sys.argv[2]
    c.output(outfile, inputs)
