test = 0
def recursion(n, step_sizes):
    global test
    for x in step_sizes:
        if x == n:
            test+=1
        elif x < n:
            recursion(n-x, step_sizes)
    return test
print(recursion(3, [1,2,3]))
