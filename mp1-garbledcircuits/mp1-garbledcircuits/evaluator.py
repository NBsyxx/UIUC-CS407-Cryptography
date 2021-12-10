"""
# Problem 1: Garbled Circuit Evaluator (10 points)
"""

import circuit
import util
import json
from circuit import BooleanCircuit
from util import KEYLENGTH, specialDecryption, specialEncryption
import codecs

decode_hex = codecs.getdecoder("hex_codec")

class GarbledCircuitEvaluator(BooleanCircuit):
    def __init__(self, from_json=None):
        # The superclass constructor initializes the gates and topological sorting
        super(GarbledCircuitEvaluator,self).__init__(from_json=from_json)

        # What remains is for us to load the garbling tables
        if from_json is not None:
            
            # Load the garbled tables
            gates = from_json["gates"]

            # TODO: your code goes here
            self.gates = gates 



    def garbled_evaluate(self, inp):
        # Precondition: initialized, topologically sorted
        #               has garbled tables
        #               inp is a mapping of wire labels for each input wire
        # Postcondition: self.wire_labels takes on labels resulting from this evaluation
        assert len(inp) == len(self.input_wires)
        self.wire_labels = {}

        # Set the wire labels for all the input wires
        for wid in self.input_wires:
            assert wid in inp, "Must provide a label for each wire"
            label = inp[wid]
            assert len(label) == 2 * 16  # Labels are keys, 16 bytes in hex
            self.wire_labels[wid] = label

        # TODO: Your code goes here
        print()
        print("input wires:")
        for k,v in inp.items():
            print(k,v)
        print()
        
        # use w1,w2 to decrypt gates["g1"]["garble_table"]
        w1key = bytes.fromhex(inp["w1"])
        w2key = bytes.fromhex(inp["w2"])

        # layer 1 
        garbled_w1_outcomes = []
        for i in range(4):
            garbled_w1_outcomes.append(specialDecryption(w1key,bytes.fromhex(self.gates["g1"]["garble_table"][i])))

        # layer 2
        for i in range(4):
            if garbled_w1_outcomes[i]!=None:
                if specialDecryption(w2key, garbled_w1_outcomes[i])!= None:
                    w5key = specialDecryption(w2key, garbled_w1_outcomes[i])
        # print("w5key",w5key)
        
        # use w3,w4 to decrypt gates["g2"]["garble_table"]
        w3key = bytes.fromhex(inp["w3"])
        w4key = bytes.fromhex(inp["w4"])

        # layer 1 
        garbled_w3_outcomes = []
        for i in range(4):
            garbled_w3_outcomes.append(specialDecryption(w3key,bytes.fromhex(self.gates["g2"]["garble_table"][i])))

        # layer 2
        for i in range(4):
            if garbled_w3_outcomes[i]!=None:
                if specialDecryption(w4key, garbled_w3_outcomes[i])!= None:
                    w6key = specialDecryption(w4key, garbled_w3_outcomes[i])
        
        self.wire_labels["w5"] =w5key.hex()
        self.wire_labels["w6"] =w6key.hex()

        # use w6,w5 to decrypt gates["g3"]["garbled_table"]

        # layer 1 
        garbled_w5_outcomes = []
        for i in range(4):
            garbled_w5_outcomes.append(specialDecryption(w5key,bytes.fromhex(self.gates["g3"]["garble_table"][i])))

        # layer 2
        for i in range(4):
            if garbled_w5_outcomes[i]!=None:
                if specialDecryption(w6key, garbled_w5_outcomes[i])!= None:
                    w7key = specialDecryption(w6key, garbled_w5_outcomes[i])
        
        print("w7key",w7key.hex())
        self.wire_labels["w7"] =w7key.hex()

        return dict((wid,self.wire_labels[wid]) for wid in self.output_wires)

        
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("usage: python evaluator.py <circuit.json>")
        sys.exit(1)

    filename = sys.argv[1]
    obj = json.load(open(filename))

    # testing
    print("testing inputs:")
    print(obj)
    print() 

    # Circuit
    c = GarbledCircuitEvaluator(from_json=obj)
    print('Garbled circuit loaded: %d gates, %d input wires, %d output_wires, %d total' \
        % (len(c.gates), len(c.input_wires), len(c.output_wires), len(c.wires)), file=sys.stderr)

    # Evaluate the circuit keys -> outputs 
    inputs = obj["inputs"]
    json.dump(c.garbled_evaluate(inputs), sys.stdout, indent=4)
    print('') # end the line
