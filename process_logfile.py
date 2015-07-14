from cat_comms import *
import sys

if len(sys.argv) < 2:
    print('''USAGE: %s <logfile>''' % sys.argv[0])
    sys.exit(-1)

logfile = open(sys.argv[1])

sess_keys = {"RM":None,
             "SM":None}

for line in logfile:
    [sm,txt_msg] = line.strip().split(' ')
    bin_msg = bytes(list(map(lambda x: int(x,16), txt_msg.split(','))))
    if is_setup(bin_msg):
        sess_keys[sm] = bin_msg[-1] & 0x0F
        proc_msg = bin_msg
    else:
        proc_msg = process_msg(bin_msg, sess_keys[sm])

    out_msg = ','.join(list(map(lambda x: hex(x)[2:], proc_msg)))
    print("%s %s" % (sm,out_msg))
