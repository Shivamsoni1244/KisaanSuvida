import pickle

model = pickle.load(open("model.pkl", "rb"))

# VERY DIFFERENT INPUTS
print(model.predict([[90,40,40,20,80,6.5,200]]))   # wet
print(model.predict([[10,10,10,35,30,5,20]]))      # dry
print(model.predict([[50,50,50,25,60,7,100]]))     # medium
