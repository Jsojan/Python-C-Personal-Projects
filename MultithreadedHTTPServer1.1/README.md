## Multithreaded HTTP server

## Short Description

The server and audit log implemented from the previous implementations were utilized  which takes the HTTP server and allows for multithreading. Note that the log file will be specified as a command line argument when running the server with -l (name of logfile) and the threadcount for number of threads to concurrently run on the server using -t with a default thread count of 4 threads. If the logfile is not found, it will be created and set with the appropriate permissions for logging each request. Furthermore, the additional functionality of the regular server and audit log must function regardless of varying coherent operations which can easily be checked with the audit log.

## Build

To build manually, type "make" with the provided Makefile on the command line to build the necessary components for this program.

## Running

To run the program, first run "./httpserver (-t optional thread count) (-l valid logfile destination) (valid port number)" where a valid port number is defined as an unsigned 32 bit interger, a log file (default will be stderr), and the number of threads to be ran which will be defaulted to 4 threads if no option is specified.

## Format

To format the files built by this porgram, type "make format" on the command line. To manually format the files, type "clang-format -i -style=file.[c,h]" to manually format the files of this program.

## Code Structure

The overall code structure for my assignment 4 follows modularization of many functions which allows for management of thread critical regions. As such, the main critical regions are the queue, HTTP request processing, audit log and response which need to be locked and unlocked as appropriate. Furthermore, the dispatcher thread will be the main() function which will push socket connection descriptors (as integers) into the queue while the worker threaders will wake up and be accept and handle the HTTP request, log and response with the next available socket connection as pertaining to the thread safe FIFO buffer. Therefore when a server descriptor connection is popped from the queue the appropriate mutex lock should be implemented to ensure no other threads are processing the request in the same critical region. In this way, this will ensure that atomicity and coherence are upheld in this program.

## Design Choices

Note, some interesting design choices that were made include ensuring mutlithreaded functionality such as using sig action instead of signal() and memcmp instead of strcmp as the thread safe versions of said functions. In addition, the choice to split up my code into several c and h files for modularization and better understanding of my code. Likewise, the threadsafe queue was included for adressing handling requests from the server and processing them into the correct responses and audit log. As such, the audit log will server as the form of validation for this server since it shows the history of responses sent by the program back to the client.

## Cleaning

To clean the files used in this program, type "make clean" on the command line. 
