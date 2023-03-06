bob = "Hello"
if (not(bob[-1] == "\n")): bob += "\n"
writer = open("test.txt", "w")
writer.write(bob)

