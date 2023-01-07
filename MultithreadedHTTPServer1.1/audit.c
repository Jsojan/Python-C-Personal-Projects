#include "audit.h"

#include <string.h>
#include <stdint.h>
#include <unistd.h>

// This is the audit log file implementation for asgn3. Note that r or rid
// represents the request ID parsed from the header file and lf or l is
// the log file descriptor which is either 2 (stderr) by default or set by
// the input file.

void handle_audit(char *s, char *m, char *u, char *sc, long r, int l) {
    // Set the string buffer to 0 to avoid null bytes in message.
    // Then pass in the apropriate response for an HTTP request audit log.
    memset(s, 0, 500);
    sprintf(s, "%s,%s,%s,%zu\n", m, u, sc, r);

    // Write the contents of the log entry to the log file
    // descriptor.
    write(l, s, strlen(s));

    return;
}
