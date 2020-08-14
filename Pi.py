
def num_steps(n, step_sizes):
    if 0 in step_sizes:
        return "0 cannot be a step size"
    test = []
    def recursion(n):
        for x in step_sizes:
            if x == n:
                test.append(1)
            elif x < n:
                recursion(n-x)
    recursion(n)
    return len(test)
print(num_steps(3,[1,2,3]))