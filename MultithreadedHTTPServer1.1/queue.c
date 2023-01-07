#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <stdbool.h>
#include <pthread.h>

#include "queue.h"

// This assignment is about building a multithreaded queue that handles
// synchronization well and enforces FIFO ordering, blocking and the
// essential properties of a queue.

// Create the struct queue to be used here.

struct queue {
    int head;
    int tail;
    int size;
    int count;

    pthread_mutex_t lock;
    pthread_cond_t wait;

    void **items;
};

// Constructor for the queue.
queue_t *queue_new(int size) {

    // Dynamically allocate space for priority queue
    queue_t *q = (queue_t *) malloc(sizeof(queue_t));

    q->size = size;

    // 0 indexed array so last element in a circular queue
    // would be size - 1 which will be used later. For now set both head
    // and tail to 0.

    q->head = 0;

    // Set the tail to negative for circular multithreaded queue.
    q->tail = 0;

    q->count = 0;

    // Initialize the mutex lock. If it fails free the associated memory
    // and return NULL.

    if (pthread_mutex_init(&q->lock, NULL) != 0) {
        free(q);
        q = NULL;
        return NULL;
    }

    // Dynamically allocate space for all potential elements to be stored in
    // this bounded buffer queue.
    q->items = calloc(size, sizeof(void *));

    // return the reference to the created queue.
    return q;
}

// Create the destructor for this queue.
void queue_delete(queue_t **q) {
    // Free the allocated for the elements then set them to NULL to protect
    // against undefined behavior.

    free((*q)->items);
    (*q)->items = NULL;

    // Unlock the mutex lock then destroy it in the destructor.
    pthread_mutex_unlock(&(*q)->lock);
    pthread_mutex_destroy(&(*q)->lock);

    // Then, free the memory allocated in q and set it to NULL.
    free(*q);
    *q = NULL;

    return;
}

// Create the push function to be used for the queue.

bool queue_push(queue_t *q, void *elem) {
    // Check if the queue pointer is NULL then return false
    if (q == NULL) {
        return false;
    }

    // If queue is full implement blocking.

    pthread_mutex_lock(&q->lock);

    // Block only if the queue is full for push.
    while (q->count >= q->size) {
        pthread_cond_wait(&q->wait, &q->lock);
    }

    // Otherwise push elem specified into the queue.
    q->items[q->tail] = elem;

    // Increment the count and tail for a circular buffer.
    q->count = q->count + 1;

    q->tail = (q->tail + 1) % q->size;

    // Unlock the mutex at this point and send the pthread condition signal.
    pthread_mutex_unlock(&q->lock);
    pthread_cond_signal(&q->wait);

    // Finally, return true.
    return true;
}

// Create the pop function to be used for this queue.

bool queue_pop(queue_t *q, void **elem) {
    // Check if the queue pointer set is Invalid then return false.
    if (q == NULL) {
        return false;
    }

    pthread_mutex_lock(&q->lock);

    // If queue is empty, implement blocking.
    while (q->count <= 0) {
        pthread_cond_wait(&q->wait, &q->lock);
    }

    // Otherwise, Dequeue the element by storing it in the elem pointer
    // for pop.

    *elem = q->items[q->head];

    // Increment the counter of the head and count for the circular queue.
    q->head = (q->head + 1) % q->size;

    q->count = q->count - 1;

    // Unlock the mutex at this point and send the pthread condition signal.
    pthread_mutex_unlock(&q->lock);
    pthread_cond_signal(&q->wait);

    // Finally, return true.
    return true;
}
