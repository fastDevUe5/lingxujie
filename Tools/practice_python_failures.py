"""Trigger every Python failure mode on purpose and compare what the editor reports.

Knowing the exact shape of each report is what makes a script failure diagnosable in one look instead
of five. This deliberately raises, logs, and prints, so the log afterwards shows the difference
between the four channels and between an exception and a clean exit.

    py "Tools/practice_python_failures.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] PYB: %s" % text)


def log_error(text):
    unreal.log_error("[LingXuJie] PYB-ERR: %s" % text)


def log_warning(text):
    unreal.log_warning("[LingXuJie] PYB-WARN: %s" % text)


def nested_three():
    raise ValueError("deliberate failure inside nested_three")


def nested_two():
    nested_three()


def nested_one():
    nested_two()


def main():
    log("=== channel comparison ===")
    log("this is unreal.log - goes to LogPython at Log verbosity")
    log_warning("this is unreal.log_warning - LogPython at Warning")
    log_error("this is unreal.log_error - LogPython at Error")
    print("this is bare print - goes through Python stdout redirection")

    log("=== exception inside a nested call chain ===")
    try:
        nested_one()
    except ValueError as error:
        # The type name alone tells you nothing about the path taken; the traceback does.
        import traceback
        log("caught: %r" % error)
        log("traceback follows:")
        for line in traceback.format_exc().split("\n"):
            if line.strip():
                log("    %s" % line)

    log("=== what an uncaught exception looks like ===")
    log("raising now; the plugin should log a traceback and continue")
    raise RuntimeError("deliberate uncaught failure")

    # Unreachable, which is itself the point: the rest of the script does not run.
    log("NOT REACHED - if you see this the uncaught raise did not stop execution")


try:
    main()
except Exception as error:  # noqa: BLE001
    # This is the wrapper every one of my scripts has; it turns a crash into a log line.
    log("outer handler caught: %r" % error)


log("AFTER THE HANDLER: execution resumed here")
