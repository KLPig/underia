import os

def w_count(_dir):
    cnt = 0
    print('(', end='')
    for l in os.listdir(_dir):
        if os.path.isdir(os.path.join(_dir, l)):
            cnt += w_count(os.path.join(_dir, l))
            print('+', end='')
        elif l.endswith('.py'):
            with open(os.path.join(_dir, l), 'r') as f:
                fr = len(f.read())
                cnt += fr
                print(str(fr) + '+', end='')
    print(')+', end='')
    return cnt

print(w_count('.'))