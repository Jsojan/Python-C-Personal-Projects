#include <stdio.h>
#include <stdint.h>
#include <string.h>

void handle_head_response(char *s, char *sc, char *sm, off_t si, int a);

void handle_get_response(char *s, char *sc, char *sm, char *rb, off_t si, int a, int f);

void handle_put_response(char *s, char *sc, char *sm, char *b, char *rb, size_t len, int a, int f);

void invalid_response(char *s, char *sc, char *sm, int a);
