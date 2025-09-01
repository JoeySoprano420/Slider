#pragma once
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef struct acs_chan acs_chan_t;
typedef struct acs_group acs_group_t;

acs_chan_t* acs_chan_new(size_t capacity);
void        acs_chan_free(acs_chan_t* ch);
void        acs_close(acs_chan_t* ch);

int         acs_send_i64(acs_chan_t* ch, long long val);
int         acs_recv_i64(acs_chan_t* ch, long long* out, int timeout_ms);

long long   acs_recv_i64_packed(acs_chan_t* ch, int timeout_ms);
int         acs_unpack_status(long long packed);
long long   acs_unpack_value(long long packed);

acs_group_t* acs_group_new(void);
void         acs_group_free(acs_group_t* g);
int          acs_group_add(acs_group_t* g, acs_chan_t* ch);
int          acs_group_size(acs_group_t* g);

long long    acs_group_select_recv_i64_packed(acs_group_t* g, int timeout_ms);
int          acs_unpack_sel_status(long long packed);
int          acs_unpack_sel_index(long long packed);
long long    acs_unpack_sel_value(long long packed);

acs_chan_t*  acs_timer_new(int period_ms, int repeat);
void         acs_sleep_ms(int ms);

typedef void* (*acs_task_fn)(void*);
int          acs_spawn(acs_task_fn fn, void* arg);

#ifdef __cplusplus
}
#endif
