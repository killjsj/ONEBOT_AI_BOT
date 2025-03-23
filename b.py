def b(*args, **kwargs):
    print("b:", args, kwargs,g)
def run(*args, **kwargs):
    b(*args, **kwargs)