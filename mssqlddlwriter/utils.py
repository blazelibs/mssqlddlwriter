import os

def mkdirs(newdir, mode=None):
    """
        a "safe" verision of makedirs() that will only create the directory
        if it doesn't already exist.  This avoids having to catch an Error
        Exception that might be a result of the directory already existing
        or might be a result of an error creating the directory.  By checking
        for the diretory first, any exception was created by the directory
        not being able to be created.
    """
    if mode is None:
        mode = 0750
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        os.makedirs(newdir, mode)
