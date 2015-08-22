from __future__ import print_function
import click
import os
import sys
import errno
import time
import atexit
import signal

PATH_PID = '/tmp/findex-gui.pid'

def start_as_daemon():

    # Double-fork to daemonize the process.
    if os.fork() > 0:
        return

    if os.fork() > 0:
        return

    # Connect SIGTERM and SIGHUP to sys.exit() so atexit gets called.    
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    signal.signal(signal.SIGHUP, lambda *_: sys.exit(0))

    # Create /tmp/findex-gui.pid automically. Fail if it already exists.
    try:
        fd = os.open(PATH_PID, os.O_CREAT | os.O_EXCL | os.O_WRONLY)

        # When process exits, clean up.
        atexit.register(lambda: os.unlink(PATH_PID))
    except OSError as e:
        if e.errno == errno.EEXIST:
            print('PID file /tmp/findex-gui.pid exists, is findex-gui already running?', file=sys.stderr)
            sys.exit(1)
        else:
            raise
    
    os.write(fd, str(os.getpid()) + '\n')
    os.close(fd)

    # Start main service.
    print('Starting the findex-gui service')
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
        with open(PATH_PID, 'r') as f:
            pid = int(f.readline().strip())
    except IOError as e:
        if e.errno == errno.ENOENT:
            print('PID file %s does not exist, is findex-gui running?' % PATH_PID)
        else:
            print('Could not read PID file %s, is findex-gui still running?' % PATH_PID, file=sys.stderr)
        sys.exit(1)

    os.kill(pid, signal.SIGHUP)
    print('Killed the findex-gui service.')


@click.command()
def restart():
    """Restart the findex-gui service."""
    
    try:
        with open(PATH_PID, 'r') as f:
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
