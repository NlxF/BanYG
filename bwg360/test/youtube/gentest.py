
l = [x *x for x in range(10)]
print(l)

g = (x*x for x in range(3))
print(next(g))
print(next(g))
print(next(g))


def gene():
    yield 'hello'
    yield 'world'
    yield '!!!'
    yield '666'
    return '!!!'


g2 = gene()

def generator():
    try:
        for item in g2:
            print('yield data')
            yield item
    finally:
        print('finally!!')
        if hasattr(g2, 'close'):
            g2.close()

gen = generator()


for item in gen:
    print(item)


def gen2(flag):
    if flag:
        yield 1
    else:
        print("what's going on")

with open('favicon.ico') as f: 
    try:
        g3 = gen2(True)
        print(next(g3))

        g4 = gen2(False)
        print(next(g4))
    finally:
        if hasattr(gen2, 'close'):
                    gen2.close()
        print('finally!!!')
