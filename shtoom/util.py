

def stack(n=None):
    import traceback
    s = traceback.extract_stack()[:-1]
    s.reverse()
    if n is not None:
        s = s[:n]
    out = []
    for file, line, method, source in s:
        for shorten in 'shtoom', 'twisted':
            if shorten+'/' in file:
                file = file[file.rfind(shorten+'/'):]
        out.append('%s:%s:%s'%(file,method,line))
    return ' '.join(out)
