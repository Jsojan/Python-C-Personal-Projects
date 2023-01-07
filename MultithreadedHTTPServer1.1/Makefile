CC = clang
CFLAGS = -Wall -Werror -Wextra -pedantic -lpthread -g

all: httpserver

httpserver: httpserver.c bind.c queue.c audit.c response.c
	$(CC) $(CFLAGS) -o httpserver httpserver.c bind.c queue.c audit.c response.c

clean: 
	rm -f httpserver *.o

format:
	clang-format -i -style=file *.[c,h]
