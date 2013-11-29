import sys

tmp_src = sys.argv[1]
tmp_tgt = sys.argv[2]

f_src = open(tmp_src, 'r')
s_src = f_src.read()
f_src.close()

l = len(s_src)
s_tgt = ''.join(['1' for _ in xrange(l)])

f_tgt = open(tmp_tgt, 'w')
f_tgt.write(s_tgt)
f_tgt.close()

