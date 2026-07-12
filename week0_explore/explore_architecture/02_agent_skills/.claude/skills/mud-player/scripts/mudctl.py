#!/usr/bin/env python3
"""mudctl - manage a persistent connection to a MUD (telnet/nc style).

A MUD is a single stateful TCP session: login, room state, and combat all live
on one continuous connection. Spawning a fresh `nc` per command loses that
state and garbles the telnet client-detection handshake. So this tool runs a
small background daemon that holds ONE socket open, answers telnet negotiation,
and streams all server output to a log file. Foreground subcommands talk to the
daemon over a Unix control socket.

Subcommands:
  start [--host H] [--port P]   connect and daemonize
  status                        is the daemon alive?
  send "<line>"                 send one command line to the MUD
  recent [-n N]                 print output received since the last read
  tail [-n N]                   print the last N lines of the whole log
  wait [--for REGEX] [-t SECS]  block until REGEX appears (or timeout), print new output
  stop                          disconnect and kill the daemon

State lives under a dir in $TMPDIR (or /tmp):
  mud.sock  control socket   mud.log  server output   mud.pid  daemon pid   mud.off  read cursor
"""
import argparse, os, re, socket, sys, time, signal, threading

STATE = os.path.join(os.environ.get("TMPDIR", "/tmp"), "mudctl")
SOCK = os.path.join(STATE, "mud.sock")
LOG = os.path.join(STATE, "mud.log")
PID = os.path.join(STATE, "mud.pid")
OFF = os.path.join(STATE, "mud.off")

IAC, DONT, DO, WONT, WILL, SB, SE = 255, 254, 253, 252, 251, 250, 240
ANSI = re.compile(rb"\x1b\[[0-9;?]*[A-Za-z]")


def strip_telnet(data, sock):
    """Remove telnet IAC sequences from data; auto-refuse negotiation so the
    server stops waiting on client detection and proceeds as an 'Unknown' client."""
    out = bytearray()
    i = 0
    while i < len(data):
        b = data[i]
        if b == IAC and i + 1 < len(data):
            cmd = data[i + 1]
            if cmd in (DO, DONT, WILL, WONT) and i + 2 < len(data):
                opt = data[i + 2]
                resp = WONT if cmd == DO else DONT if cmd == WILL else None
                if resp is not None:
                    try:
                        sock.sendall(bytes([IAC, resp, opt]))
                    except OSError:
                        pass
                i += 3
                continue
            if cmd == SB:  # subnegotiation: skip until IAC SE
                j = i + 2
                while j + 1 < len(data) and not (data[j] == IAC and data[j + 1] == SE):
                    j += 1
                i = j + 2
                continue
            i += 2
            continue
        out.append(b)
        i += 1
    return bytes(out)


def daemon(host, port):
    s = socket.create_connection((host, port), timeout=10)
    s.settimeout(0.5)
    ctl = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    if os.path.exists(SOCK):
        os.unlink(SOCK)
    ctl.bind(SOCK)
    ctl.listen(5)
    ctl.settimeout(0.5)
    logf = open(LOG, "ab", buffering=0)
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            try:
                data = s.recv(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            if not data:
                break
            logf.write(strip_telnet(data, s))
        stop.set()

    threading.Thread(target=reader, daemon=True).start()

    while not stop.is_set():
        try:
            conn, _ = ctl.accept()
        except socket.timeout:
            continue
        except OSError:
            break
        with conn:
            msg = conn.recv(65536)
            if msg == b"__STOP__":
                stop.set()
                break
            try:
                s.sendall(msg)
            except OSError:
                stop.set()
                break
    try:
        s.close()
    finally:
        for p in (SOCK, PID):
            if os.path.exists(p):
                os.unlink(p)


def is_alive():
    if not os.path.exists(PID):
        return False
    try:
        pid = int(open(PID).read())
        os.kill(pid, 0)
        return os.path.exists(SOCK)
    except (OSError, ValueError):
        return False


def cmd_start(a):
    if is_alive():
        print("already running")
        return
    os.makedirs(STATE, exist_ok=True)
    for p in (LOG, OFF):
        if os.path.exists(p):
            os.unlink(p)
    pid = os.fork()
    if pid > 0:
        with open(PID, "w") as f:
            f.write(str(pid))
        for _ in range(40):
            if os.path.exists(SOCK):
                break
            time.sleep(0.1)
        time.sleep(1.5)  # let the login banner arrive
        print(f"connected to {a.host}:{a.port} (pid {pid})")
        print("--- initial output ---")
        _print_recent(999)
        return
    os.setsid()
    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(devnull, fd)
    daemon(a.host, a.port)
    os._exit(0)


def _send_raw(msg):
    c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    c.connect(SOCK)
    c.sendall(msg)
    c.close()


def cmd_send(a):
    if not is_alive():
        print("not connected. run: mudctl.py start", file=sys.stderr)
        sys.exit(1)
    _send_raw(a.line.encode() + b"\n")
    time.sleep(a.pause)
    _print_recent(999)


def _read_off():
    try:
        return int(open(OFF).read())
    except (OSError, ValueError):
        return 0


def _print_recent(maxlines):
    if not os.path.exists(LOG):
        return
    size = os.path.getsize(LOG)
    off = _read_off()
    if off > size:
        off = 0
    with open(LOG, "rb") as f:
        f.seek(off)
        data = f.read()
    with open(OFF, "w") as f:
        f.write(str(size))
    text = ANSI.sub(b"", data).decode("utf-8", "replace")
    lines = text.splitlines()
    if len(lines) > maxlines:
        lines = lines[-maxlines:]
    print("\n".join(lines))


def cmd_recent(a):
    _print_recent(a.n)


def cmd_tail(a):
    if not os.path.exists(LOG):
        return
    data = open(LOG, "rb").read()
    text = ANSI.sub(b"", data).decode("utf-8", "replace")
    print("\n".join(text.splitlines()[-a.n:]))
    with open(OFF, "w") as f:
        f.write(str(os.path.getsize(LOG)))


def cmd_wait(a):
    """Block until REGEX appears in new output or timeout, then print new output."""
    pat = re.compile(a.pattern, re.I) if a.pattern else None
    deadline = time.time() + a.timeout
    start_off = _read_off()
    while time.time() < deadline:
        size = os.path.getsize(LOG) if os.path.exists(LOG) else 0
        if size > start_off:
            with open(LOG, "rb") as f:
                f.seek(start_off)
                text = ANSI.sub(b"", f.read()).decode("utf-8", "replace")
            if pat is None or pat.search(text):
                break
        time.sleep(0.3)
    _print_recent(999)


def cmd_status(a):
    print("connected" if is_alive() else "not connected")


def cmd_stop(a):
    if not is_alive():
        print("not connected")
        return
    try:
        _send_raw(b"__STOP__")
    except OSError:
        pass
    time.sleep(0.5)
    if os.path.exists(PID):
        try:
            os.kill(int(open(PID).read()), signal.SIGTERM)
        except (OSError, ValueError):
            pass
    print("disconnected")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start"); s.add_argument("--host", default="localhost"); s.add_argument("--port", type=int, default=4000); s.set_defaults(fn=cmd_start)
    s = sub.add_parser("send"); s.add_argument("line"); s.add_argument("--pause", type=float, default=1.0); s.set_defaults(fn=cmd_send)
    s = sub.add_parser("recent"); s.add_argument("-n", type=int, default=999); s.set_defaults(fn=cmd_recent)
    s = sub.add_parser("tail"); s.add_argument("-n", type=int, default=40); s.set_defaults(fn=cmd_tail)
    s = sub.add_parser("wait"); s.add_argument("--for", dest="pattern", default=None); s.add_argument("-t", "--timeout", type=float, default=5.0); s.set_defaults(fn=cmd_wait)
    s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("stop"); s.set_defaults(fn=cmd_stop)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
