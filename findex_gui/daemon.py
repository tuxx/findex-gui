from __future__ import print_function
import click
import os
import sys
import errno
import time
import atexit
import signal


def start_as_daemon():
    # Double-fork to daemonize the process.
    if os.fork() > 0:
        return
    
    if os.fork() > 0:
        return


    # Connect SIGTERM and SIGHUP to sys.exit() so atexit gets called.    
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    signal.signal(signal.SIGHUP, lambda *_: sys.exit(0))

    # Create /tmp/findex-gui.pid atomically. Fail if it already exists.
    try:
        fd = os.open('/tmp/findex-gui.pid', os.O_CREAT | os.O_EXCL | os.O_WRONLY)

        # When process exits, clean up.
        atexit.register(lambda: os.unlink('/tmp/findex-gui.pid'))
    except OSError as e:
        if e.errno == errno.EEXIST:
            print('PID file /tmp/findex-gui.pid exists, is findex-gui already running?', file=sys.stderr)
            sys.exit(1)
        else:
            raise
    os.write(fd, str(os.getpid()) + '\n')
    os.close(fd)

    # Start main service.
    from findex_gui.__main__ import main
    main()


@click.group()
def cli():
    pass


@click.command()
def start():
    """Start the findex-gui service."""
    start_as_daemon()


@click.command()
def stop():
    """Stop the findex-gui service."""

    # Try to read PID file.
    try:
        with open('/tmp/findex-gui.pid', 'r') as f:
            pid = int(f.readline().strip())
    except IOError as e:
        print('Could not read PID file, is findex-gui still running?', file=sys.stderr)
        sys.exit(1)

    os.kill(pid, signal.SIGHUP)


@click.command()
def restart():
    """Restart the findex-gui service."""
    
    try:
        with open('/tmp/findex-gui.pid', 'r') as f:
            pid = int(f.readline().strip())
            os.kill(pid, signal.SIGHUP)
    except IOError as e:
        print('findex-gui not running, starting it.', file=sys.stderr)

    start_as_daemon()

        
cli.add_command(start)
cli.add_command(stop)
cli.add_command(restart)


if __name__ == '__main__':
    cli()
