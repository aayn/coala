import calendar
import time
import hashlib

from coalib.misc.CachingUtilities import (
    pickle_load, pickle_dump, time_consistent, update_time_db,
    delete_cache_files)


class FileCache:

    def __init__(self, log_printer, project_dir, flush_cache=False):
        """
        Initialize cache instance for project. Example usage:

        >>> from pyprint.NullPrinter import NullPrinter
        >>> from coalib.output.printers.LogPrinter import LogPrinter
        >>> import copy, time
        >>> log_printer = LogPrinter(NullPrinter())

        >>> cache = FileCache(log_printer, "coala_test", flush_cache=True)
        >>> cache.track_new_files(["a.c", "b.c"])
        >>> cache.write()

        >>> time.sleep(1)
        >>> cache = FileCache(log_printer, "coala_test", flush_cache=False)
        >>> old_data = copy.deepcopy(cache.last_cache())
        >>> cache.add_to_changed_files({"a.c"})
        >>> cache.write()

        >>> cache = FileCache(log_printer, "coala_test", flush_cache=False)
        >>> new_data = cache.last_cache()
        >>> old_data["a.c"] == new_data["a.c"]
        True
        >>> old_data["b.c"] < new_data["b.c"]
        True

        :param log_printer: A LogPrinter object to use for logging.
        :param project_dir: The root directory of the project to be used
                            as a key identifier.
        :param flush_cache: Flush the cache and rebuild it.
        """
        self.log_printer = log_printer
        self.project_dir = project_dir.encode("utf-8")
        self.md5sum = hashlib.md5(self.project_dir).hexdigest()
        self.current_time = calendar.timegm(time.gmtime())
        if not time_consistent(log_printer, self.md5sum):
            log_printer.warn("It seems like you went back in time - your "
                             "system time is behind the last recorded run "
                             "time on this project. The cache will "
                             "be flushed and rebuilt.")
            flush_cache = True
        if not flush_cache:
            self.data = pickle_load(log_printer, self.md5sum, {})
        else:
            self.data = {}
            delete_cache_files(log_printer, [self.md5sum])
            log_printer.info("The file cache was successfully flushed.")
        self.changed_files = set()

    def write(self):
        """
        Update the last run time on the project for each file
        to the current time.
        """
        for file_name in self.data:
            if (self.data[file_name] == -1 or
                    file_name not in self.changed_files):
                self.data[file_name] = self.current_time
        pickle_dump(self.log_printer, self.md5sum, self.data)
        update_time_db(self.log_printer, self.md5sum, self.current_time)
        self.changed_files = set()

    def add_to_changed_files(self, changed_files):
        """
        Keep track of changed files in ``changed_files`` for future use in
        ``write``.

        :param changed_files: A set of files that had changed since the last
                              run time.
        """
        self.changed_files.update(changed_files)

    def last_cache(self):
        """
        Get the last run time on the project in epoch format
        (number of seconds since Jan 1, 1970).

        :return: Returns a dict of files with file path as key
                 and the last run time on that file as value.
                 Returns None if this is the first time on that project.
        """
        return self.data

    def track_new_files(self, new_files):
        """
        Start tracking new files given in ``new_files`` by adding them to the
        database.

        :param new_files: The list of new files that need to be tracked.
                          These files are initialized with their last
                          modified tag as -1.
        """
        for new_file in new_files:
            self.data[new_file] = -1
