import random, time

common = 0
uncommon = 0
rare = 0
ultraRare = 0
superRare = 0

iterations = 100000000

def returnChance(denominator, numerator=1):
    if random.randint(numerator,denominator) == 1:
        return True
    else:
        return False

print("Running tests...")

t = time.process_time()

for i in range(1,iterations):
    if i%5 == 0:
        uncommon+=1
    elif returnChance(400) is True:
        superRare += 1
    elif returnChance(50) is True:
        ultraRare += 1 
    elif returnChance(15) is True:
        rare += 1
    elif returnChance(10) is True:
        uncommon += 1
    else:
        common +=1
    print(f"Progress: {i}/{iterations}")

def getPercentage(n):
    return n/iterations*100

print("Roll Rates")
print("--------------------------------------------------")
print(f"Common: {common} ({round(getPercentage(common),1)}%)")
print(f"Uncommon: {uncommon} ({round(getPercentage(uncommon),1)}%)")
print(f"Rare: {rare} ({round(getPercentage(rare),1)}%)")
print(f"Ultra Rare: {ultraRare} ({round(getPercentage(ultraRare),1)}%)")
print(f"Super Rare: {superRare} ({round(getPercentage(superRare),1)}%)")
print("--------------------------------------------------")

elapsedTime = time.process_time() - t

print (f"Process took {elapsedTime} seconds.")


    