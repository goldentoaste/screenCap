

keyWrap = ""
valueWrap = "\""


output = ""
varName = input("dictionaryName:")
output = f"{varName} = {{\n"

def wrap(s, w):
    return w + s + w

print("Input next space serpated pair, or exit to finish")

while True:
    pair = input("> ")

    if pair == "exit":
        break

    pair = pair.split(" ")
    pair[0] = "0x"+pair[0]
    output += f"{wrap(str(int(pair[0],16)), keyWrap)}:{wrap(pair[1], valueWrap)},\n"


output += "}"

print(output)
input("Done. Press enter to close window.")
