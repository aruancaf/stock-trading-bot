import os

vers = []
model_name = "trading_modelV"
for i in os.listdir():
    if model_name in i:
        vers.append(int(i.replace(model_name, "").replace(".h5", "")))

print(max(vers) + 1)
