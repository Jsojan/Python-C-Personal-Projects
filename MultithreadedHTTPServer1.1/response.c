#include "response.h"

#include <string.h>
#include <stdint.h>
#include <unistd.h>

void handle_head_response(char *s, char *sc, char *sm, off_t si, int a) {

    // Return the appropriate response for a HEAD request.
    memset(s, 0, 500);
    sprintf(s, "HTTP/1.1 %s %s\r\nContent-Length: %zu\r\n\r\n", sc, sm, si);

    write(a, s, strlen(s));
    return;
}

void handle_get_response(char *s, char *sc, char *sm, char *rb, off_t si, int a, int f) {
    // Return the appropriate response for a GET request.
    memset(s, 0, 500);
    sprintf(s, "HTTP/1.1 %s %s\r\nContent-Length: %zu\r\n\r\n", sc, sm, si);
    write(a, s, strlen(s));

    // Store the number of bytes left to be read.
    int ze = 0;

    // Check if the number of bytes left to read
    // still exist.

    while ((ze = read(f, rb, 2048)) > 0) {
        write(a, rb, ze);
    }

    return;
}

void handle_put_response(char *s, char *sc, char *sm, char *b, char *rb, size_t len, int a, int f) {

    // Return the appropriate response for a PUT request.
    memset(s, 0, 500);
    sprintf(s, "HTTP/1.1 %s %s\r\nContent-Length: %zu\r\n\r\n%s\n", sc, sm, (size_t) strlen(sm) + 1,
        sm);

    // Special edge case if the message body was already read into
    // the buffer if the whole message was less than or equal to
    // 2048 bytes.

    if (len < 2048) {
        // String slicing for message body
        char *slice = b + (strlen(b) - len);

        // Write the message body to the file and the response
        // back to the file descriptor.
        write(f, slice, strlen(slice));
        write(a, s, strlen(s));

        // Close both files and skip to next request.
        return;
    }

    size_t t = 0;
    size_t check = 0;

    // Loop through calls of read from the message body into the
    // buffer and write the contents of the buffer until nothing more
    // can be read.

    while ((t = read(a, rb, 2048)) > 0) {
        write(f, rb, t);
        check += t;

        if (check == len) {
            break;
        }
    }

    write(a, s, strlen(s));

    return;
}

void invalid_response(char *s, char *sc, char *sm, int a) {
    memset(s, 0, 500);

    sprintf(s, "HTTP/1.1 %s %s\r\nContent-Length: %zu\r\n\r\n%s\n", sc, sm, (size_t) strlen(sm) + 1,
        sm);

    write(a, s, strlen(s));

    // Only close a valid file in case file is not found. Don't
    // want to close stdin, stdout or stderr hence greater than 2
    // only.
    return;
}
