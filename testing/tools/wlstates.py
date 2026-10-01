# Minimal Wayland client: opens one xdg toplevel and prints the states in every configure.
import socket, struct, os, sys, time
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(os.path.join(os.environ['XDG_RUNTIME_DIR'], os.environ['WAYLAND_DISPLAY']))
nid = [2]
def new():
    nid[0] += 1; return nid[0]
def send(obj, op, payload=b''):
    sock.sendall(struct.pack('<II', obj, ((8 + len(payload)) << 16) | op) + payload)
def wstr(s):
    b = s.encode() + b'\0'; pad = (4 - len(b) % 4) % 4
    return struct.pack('<I', len(b)) + b + b'\0' * pad
REG = 2
send(1, 1, struct.pack('<I', REG))          # wl_display.get_registry
buf = b''
def events(timeout):
    global buf
    sock.settimeout(timeout)
    try:
        while True:
            buf += sock.recv(65536)
            while len(buf) >= 8:
                obj, so = struct.unpack('<II', buf[:8]); size, op = so >> 16, so & 0xffff
                if len(buf) < size: break
                body, buf = buf[8:size], buf[size:]
                yield obj, op, body
    except socket.timeout:
        return
globals_ = {}
for obj, op, body in events(0.5):
    if obj == REG and op == 0:
        name, = struct.unpack('<I', body[:4]); l, = struct.unpack('<I', body[4:8])
        iface = body[8:8 + l - 1].decode(); ver, = struct.unpack('<I', body[8 + ((l + 3) & ~3):][:4])
        globals_[iface] = (name, ver)
def bind(iface, ver):
    name, v = globals_[iface]; oid = new()
    send(REG, 0, struct.pack('<I', name) + wstr(iface) + struct.pack('<II', min(ver, v), oid)); return oid
comp = bind('wl_compositor', 4); wm = bind('xdg_wm_base', 2); shm = bind('wl_shm', 1); drawn=[False]; cmd=[None]; t0=time.time()
surf = new(); send(comp, 0, struct.pack('<I', surf))
xs = new(); send(wm, 2, struct.pack('<II', xs, surf))
top = new(); send(xs, 1, struct.pack('<I', top))
send(top, 2, wstr('hftest-raw')); send(top, 3, wstr('hftest.raw'))
send(surf, 6)                                # commit
NAMES = {1:'maximized',2:'fullscreen',3:'resizing',4:'activated',5:'tiled_left',6:'tiled_right',7:'tiled_top',8:'tiled_bottom',9:'suspended'}
end = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 2)
plan = sys.argv[2:]          # e.g. max@1.5 unmax@3
while time.time() < end:
    for p in list(plan):
        what, at = p.split('@')
        if time.time() > t0 + float(at):
            plan.remove(p); print('--> app asks', what, flush=True)
            send(top, 9 if what == 'max' else 10)
    for obj, op, body in events(0.3):
        if obj == wm and op == 0: send(wm, 3, body[:4])               # pong
        elif obj == top and op == 0:
            w, h, n = struct.unpack('<iiI', body[:12])
            st = struct.unpack('<%dI' % (n // 4), body[12:12 + n])
            print('configure', w, h, [NAMES.get(s, s) for s in st], flush=True)
        elif obj == xs and op == 0:
            send(xs, 4, body[:4])                                     # ack_configure
            if not drawn[0]:
                drawn[0] = True
                W, H = 400, 300
                fd = os.memfd_create('buf'); os.ftruncate(fd, W * H * 4); os.write(fd, b'\x40' * (W * H * 4))
                pool = new()
                m = struct.pack('<II', shm, ((8 + 8) << 16) | 0) + struct.pack('<Ii', pool, W * H * 4)
                sock.sendmsg([m], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack('i', fd))])
                b = new(); send(pool, 0, struct.pack('<IiiiiI', b, 0, W, H, W * 4, 1))
                send(surf, 1, struct.pack('<Iii', b, 0, 0))
            send(surf, 6)
            if cmd[0] and time.time() > t0 + 1.5:
                pass

