#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <err.h>
#include <errno.h>

#include <sys/socket.h>
#include <sys/stat.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <getopt.h>
#include <signal.h>

#include "bind.h"
#include "response.h"
#include "audit.h"
#include "queue.h"

#define BUFSIZE 2048

// Define a global variable for the log file descriptor.
// Default will be 2 for stderr.
int lf = 2;

// Same for the queue descriptor for the threadpool queue.
queue_t *q = NULL;

// Create a signal handler function to be used when SIGINT or SIGTERM
// is detected in the code.

void handle_signal(int signum) {
    if (signum == SIGTERM || signum == SIGINT) {
        // Only close the log file if lf is not stderr and was specified aka
        // it's descriptor will be greater than 2.
        if (lf > 2) {
            close(lf);
        }

        // Call sync function here.
        sync();

        // Free the queue allocated on interrupt.
        if (q != NULL) {
            queue_delete(&q);
        }

        // Then exit since SIGINT or SIGTERM was detected.
        exit(EXIT_SUCCESS);
    }
}

void handle_process(int lf, int afd) {
    char buf[BUFSIZE] = "";
    char rbuf[BUFSIZE] = "";

    memset(buf, 0, BUFSIZE);
    struct stat st;

    // Begin reading the HTTP headers using read()

    char *rdelim = "\r\n\r\n";
    char *result = "";

    // Space delimeter for strtok_r
    char *delim = " ";

    char *ndelim = "\n";
    char *context = buf;

    // Default status code unless invalid issue.
    char *scode = "200";
    char *smessage = "OK";

    ssize_t byte_count = 0;

    // Use recv to read in data to buffer

    // TA Eric helped me with reading into the buffer on 10/19/22 during
    // his office hours in person.

    ssize_t bytes_read = 0;

    do {
        bytes_read = read(afd, buf, BUFSIZE);
        byte_count += bytes_read;
    }

    while (bytes_read > 0 && (result = strstr(buf, rdelim)) == NULL);

    // Acquiring the method from the buffer and checking its validity.
    char s[BUFSIZE] = "";
    // memset(s, 0, BUFSIZE);
    strcpy(s, buf);

    char sr[500] = "";
    memset(sr, 0, 500);

    char *method = strtok_r(s, delim, &context);

    if (method == NULL) {
        return;
    }

    // Acquiring the URI from the buffer and checking its validity.

    if (strlen(method) > 8) {
        scode = "500";
        smessage = "Internal Server Error";
    }

    if (memcmp(method, "GET", 3) != 0 && memcmp(method, "HEAD", 4) != 0
        && memcmp(method, "PUT", 3) != 0) {
        scode = "500";
        smessage = "Internal Server Error";
    }

    char *uri = strtok_r(NULL, delim, &context);

    // Special case to handle garbage request in which the 400, Bad Request
    // is sent and the program closes the file descriptor without
    // ending the program.

    if (uri == NULL) {
        scode = "500";
        smessage = "Internal Server Error";

        memset(sr, 0, 500);

        sprintf(sr, "HTTP/1.1 %s %s\r\nContent-Length: %ld\r\n\r\n%s\n", scode, smessage,
            strlen(smessage) + 1, smessage);

        write(afd, sr, strlen(sr));

        close(afd);
        return;
    }

    if (uri[0] != '/' || strlen(uri) > 19) {
        scode = "500";
        smessage = "Internal Server Error";
    }

    // Check the HTTP version number and ensure it matches.
    char *version = strtok_r(NULL, ndelim, &context);
    char *v = "HTTP/1.1";

    if (version == NULL) {
        scode = "500";
        smessage = "Internal Server Error";
    }

    if (*version != *v) {
        scode = "500";
        smessage = "Internal Server Error";
    }

    // Begin parsing the message header-field

    char *token = strtok_r(NULL, ndelim, &context);

    // Set default Content Length to 0.
    size_t length = 0;

    // Set default request ID value to 0
    long rid = 0;

    char key[100] = "";
    char val[100] = "";
    bool errcheck = true;

    // While /r/n/r/n is not in the header field
    // TA Gurpreet helped me with the loop conditional check
    // on 10/21/22.

    while (strstr(token, rdelim) == NULL) {
        if (strlen(token) == 1) {
            break;
        }

        sscanf(token, "%s%s", key, val);
        // Check for a request-id and store that value as well.

        if (memcmp(key, "st-Id:", 6) == 0 || memcmp(key, "1.1", 3) == 0) {
            rid = strtoul(val, NULL, 10);

            if (rid < 3) {
                rid += 1;
            }

            else {
                rid = 1;
            }

            errcheck = false;
        }

        if (memcmp(key, "Request-Id:", 11) == 0) {
            rid = strtoul(val, NULL, 10);
            errcheck = false;
        }

        // Check for the content length value.
        if (memcmp(key, "Content-Length:", 15) == 0) {
            sscanf(val, "%zu", &length);
            if (memcmp(method, "GET", 3) == 0) {
                errcheck = true;
            }
        }

        token = strtok_r(NULL, ndelim, &context);

        if (token == NULL) {
            break;
        }
    }

    int f1 = 0;

    // Check if the file pointed to by a PUT request is valid, else
    // create the file specified and set scode to 201.

    if (memcmp(method, "PUT", 3) == 0) {
        if ((f1 = open(uri + 1, O_DIRECTORY, 0)) != -1) {
            scode = "500";
            smessage = "Internal Server Error";
        }

        else if (access(uri + 1, F_OK) != 0) {
            f1 = open(uri + 1, O_WRONLY | O_CREAT | O_TRUNC, 0664);
            scode = "201";
            smessage = "Created";
        }

        else {
            f1 = open(uri + 1, O_WRONLY | O_TRUNC);
            scode = "200";
            smessage = "OK";
        }

        fstat(f1, &st);
    }

    // Open the file pointed to the URI for GET and HEAD.

    int f2 = 0;

    // Check the file can be accessed for GET and HEAD requests.
    if (memcmp(method, "GET", 3) == 0 || memcmp(method, "HEAD", 4) == 0) {
        if ((f2 = open(uri + 1, O_DIRECTORY, 0)) != -1) {
            scode = "500";
            smessage = "Internal Server Error";
        }

        else if ((f2 = open(uri + 1, O_RDONLY, 0)) == -1) {
            scode = "404";
            smessage = "Not Found";
        }

        else {
            scode = "200";
            smessage = "OK";
        }

        fstat(f2, &st);
    }
    // Acquire the size of the file when needed.
    off_t size = st.st_size;

    // Write the Audit log here if the audit log option was speciifed
    // on the command line.

    handle_audit(sr, method, uri, scode, rid, lf);

    // Return appropriate response if the scode is not valid for
    // responses.

    if (memcmp(scode, "200", 3) != 0 && memcmp(scode, "201", 3) != 0) {
        invalid_response(sr, scode, smessage, afd);

        close(afd);
        return;
    }

    // Return the appropriate response for a HEAD request

    else if (memcmp(method, "HEAD", 4) == 0) {
        handle_head_response(sr, scode, smessage, size, afd);

        close(f2);
        close(afd);
        return;
    }

    // Return the appropriate response for a GET request

    else if (memcmp(method, "GET", 3) == 0) {
        handle_get_response(sr, scode, smessage, rbuf, size, afd, f2);

        close(f2);
        close(afd);
        return;
    }

    // Return tbe appropriate response for a PUT request.

    else if (memcmp(method, "PUT", 3) == 0) {
        handle_put_response(sr, scode, smessage, buf, rbuf, length, afd, f1);
        close(f1);
        close(afd);
        return;
    }

    return;
}

// Create a thread function for the threads to use

void *thread_function() {
    while (1) {
        // Pop the next available socket connection and type cast it back to an int.
        void *l;
        queue_pop(q, &l);
        int cond = (int) l;
        if (l != NULL) {
            // Connection was ensured and work needs to be done.
            handle_process(lf, cond);
        }
    }
}

// This program essentially creates an HTTP server that handles GET, PUT, and
// HEAD functions. In addition, the server needs to deal with requests
// and return error codes apropriately.

int main(int argc, char *argv[]) {
    // Use the signal handler function for SIGINT and SIGTERM in the code.
    signal(SIGTERM, handle_signal);
    signal(SIGINT, handle_signal);

    uint16_t portnum;

    // Socket Descriptor int.
    int sd;

    // Accepted File Descriptor.
    int afd;

    errno = 0;

    // Check that the number of arguments are valid.
    if (argc < 2) {
        errx(1, "not enough arguments\nusage: ./httpserver <-t threads> <-l logfile> <uint16_t "
                "port number>");
    }

    // Create opt and set default threadcoutn to 4.
    int opt = 0;
    uint32_t threadcount = 4;

    // Create get opt loop to parse if there is threads or a log file.

    while ((opt = getopt(argc, argv, "t:l:")) != -1) {
        switch (opt) {
        case 't': {
            // If threadcount is not 4 then set it to the specified
            // value.
            threadcount = strtoul(optarg, NULL, 10);
            break;
        }
        case 'l': {
            // May need to change permissions of log file later. Reminder
            // to close this file after each log has been added.
            lf = open(optarg, O_CREAT | O_RDWR, 0644);
            break;
        }
        default: {
            // Return if invalid option is chosen.
            return 1;
        }
        }
    }

    // Create the new allocated queue which will be of threadsize not
    // including the dispatcher thread which will be created in this file.

    q = queue_new(10);

    if (q == NULL) {
        return 1;
    }

    // Create the worker threads
    pthread_t tpool[threadcount];

    for (uint32_t i = 0; i < threadcount; i++) {
        pthread_create(&tpool[i], NULL, thread_function, NULL);
    }

    char *port = argv[argc - 1];

    portnum = strtoul(port, &port, 10);

    // Check if the port number supplied can be converted to a uint16_t port
    // number.

    if (*port != '\0') {
        errx(1, "invalid port number: %s", argv[1]);
    }

    sd = create_listen_socket(portnum);

    // Infinite Loop

    while (true) {
        if ((afd = accept(sd, NULL, NULL)) < 0) {
            warn("bind: Already in use");
            return 1;
        }

        // Perform the HTTP processing here.
        handle_process(lf, afd);
    }

    // End of program if succesful.
    return 0;
}
