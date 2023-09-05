import sys
import os

print(sys.argv)

if __name__ == '__main__':
    # args = sys.argv[1:]
    # match args:
    #     case arg1, arg2:
    #         print(f"Args: {arg1}, {arg2}")
    #     case "Hello", *args:
    #         print(f"Hello from {args}")

    # args = sys.argv
    # #arg1 = args[1]
    # for a in args[1:]:
    #     print(a)
    # x = [1]
    # iter_ = iter(x[1:])
    # print(iter_)
    # next(iter_)

    env_vars = os.environ[""]
    print(env_vars)
