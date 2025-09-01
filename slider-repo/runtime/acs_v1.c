#include "acs_v1.h"
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

struct acs_chan { long long* buf; size_t cap, head, tail; int closed;
    pthread_mutex_t mu; pthread_cond_t not_empty, not_full; };
struct acs_group { acs_chan_t** chans; int n, cap; };

static int timedwait_ms(pthread_cond_t* cv, pthread_mutex_t* mu, int timeout_ms){
    if (timeout_ms < 0) return pthread_cond_wait(cv, mu);
    struct timespec ts; clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_ms/1000; ts.tv_nsec += (timeout_ms%1000)*1000000LL;
    if (ts.tv_nsec >= 1000000000L) { ts.tv_sec += 1; ts.tv_nsec -= 1000000000L; }
    return pthread_cond_timedwait(cv, mu, &ts);
}
static int is_full(acs_chan_t* ch){ return ((ch->head+1)%ch->cap)==ch->tail; }
static int is_empty(acs_chan_t* ch){ return ch->head==ch->tail; }

acs_chan_t* acs_chan_new(size_t capacity){
    if (capacity<1) capacity=1;
    acs_chan_t* ch=(acs_chan_t*)calloc(1,sizeof(*ch));
    ch->buf=(long long*)malloc(sizeof(long long)*(capacity+1));
    ch->cap=capacity+1; ch->head=ch->tail=0; ch->closed=0;
    pthread_mutex_init(&ch->mu,NULL);
    pthread_cond_init(&ch->not_empty,NULL);
    pthread_cond_init(&ch->not_full,NULL);
    return ch;
}
void acs_chan_free(acs_chan_t* ch){
    if(!ch) return;
    pthread_mutex_destroy(&ch->mu);
    pthread_cond_destroy(&ch->not_empty);
    pthread_cond_destroy(&ch->not_full);
    free(ch->buf); free(ch);
}
void acs_close(acs_chan_t* ch){
    pthread_mutex_lock(&ch->mu); ch->closed=1;
    pthread_cond_broadcast(&ch->not_empty);
    pthread_cond_broadcast(&ch->not_full);
    pthread_mutex_unlock(&ch->mu);
}
int acs_send_i64(acs_chan_t* ch, long long val){
    pthread_mutex_lock(&ch->mu);
    while(!ch->closed && is_full(ch)) pthread_cond_wait(&ch->not_full,&ch->mu);
    if(ch->closed){ pthread_mutex_unlock(&ch->mu); return -1; }
    ch->buf[ch->head]=val; ch->head=(ch->head+1)%ch->cap;
    pthread_cond_signal(&ch->not_empty);
    pthread_mutex_unlock(&ch->mu);
    return 1;
}
int acs_recv_i64(acs_chan_t* ch, long long* out, int timeout_ms){
    pthread_mutex_lock(&ch->mu);
    while(!ch->closed && is_empty(ch)){
        int r=timedwait_ms(&ch->not_empty,&ch->mu,timeout_ms);
        if(timeout_ms>=0 && r!=0){ pthread_mutex_unlock(&ch->mu); return 0; }
    }
    if(is_empty(ch) && ch->closed){ pthread_mutex_unlock(&ch->mu); return -1; }
    *out=ch->buf[ch->tail]; ch->tail=(ch->tail+1)%ch->cap;
    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->mu);
    return 1;
}
long long acs_recv_i64_packed(acs_chan_t* ch, int timeout_ms){
    long long v=0; int r = acs_recv_i64(ch,&v,timeout_ms);
    unsigned long long status = (r==1)?0ULL : (r==0?1ULL:2ULL);
    unsigned long long uv = ((unsigned long long)v) & ((1ULL<<62)-1);
    return (long long)((status<<62) | uv);
}
int acs_unpack_status(long long p){ return (int)(((unsigned long long)p)>>62); }
long long acs_unpack_value(long long p){
    unsigned long long uv = ((unsigned long long)p) & ((1ULL<<62)-1);
    if(uv & (1ULL<<61)) uv |= (3ULL<<62);
    return (long long)uv;
}

acs_group_t* acs_group_new(void){
    acs_group_t* g=(acs_group_t*)calloc(1,sizeof(*g));
    g->cap=8; g->chans=(acs_chan_t**)calloc(g->cap,sizeof(acs_chan_t*)); return g;
}
void acs_group_free(acs_group_t* g){ if(!g) return; free(g->chans); free(g); }
int acs_group_add(acs_group_t* g, acs_chan_t* ch){
    if(g->n==g->cap){ g->cap*=2; g->chans=(acs_chan_t**)realloc(g->chans,sizeof(acs_chan_t*)*g->cap); }
    g->chans[g->n]=ch; return g->n++;
}
int acs_group_size(acs_group_t* g){ return g->n; }

long long acs_group_select_recv_i64_packed(acs_group_t* g, int timeout_ms){
    if(!g || g->n==0) return (long long)(1ULL<<62); // timeout
    long long v;
    for(int i=0;i<g->n;i++){
        int r=acs_recv_i64(g->chans[i], &v, 0);
        if(r==1){ unsigned long long st=0, idx=i&0x3F, val=((unsigned long long)v)&((1ULL<<56)-1);
            return (long long)((st<<62)|(idx<<56)|val); }
    }
    if(timeout_ms==0) return (long long)(1ULL<<62);
    const int step=1; int waited=0; int allclosed=0;
    while(timeout_ms<0 || waited<timeout_ms){
        allclosed=1;
        for(int i=0;i<g->n;i++){
            int r=acs_recv_i64(g->chans[i], &v, 1);
            if(r==1){ unsigned long long st=0, idx=i&0x3F, val=((unsigned long long)v)&((1ULL<<56)-1);
                return (long long)((st<<62)|(idx<<56)|val); }
            else if(r==0){ allclosed=0; }
        }
        if(allclosed) return (long long)((2ULL<<62));
        waited+=step;
    }
    return (long long)(1ULL<<62);
}
int acs_unpack_sel_status(long long p){ return (int)(((unsigned long long)p)>>62); }
int acs_unpack_sel_index(long long p){ return (int)((((unsigned long long)p)>>56)&0x3F); }
long long acs_unpack_sel_value(long long p){
    unsigned long long uv = ((unsigned long long)p)&((1ULL<<56)-1);
    if(uv & (1ULL<<55)) uv |= (0xFFULL<<56);
    return (long long)uv;
}

struct timer_args { acs_chan_t* out; int period_ms; int repeat; };
static void* timer_thread(void* vp){
    struct timer_args* a=(struct timer_args*)vp; long long tick=0;
    do{
        struct timespec ts = { a->period_ms/1000, (a->period_ms%1000)*1000000L };
        nanosleep(&ts,NULL);
        acs_send_i64(a->out, ++tick);
    } while(a->repeat);
    acs_close(a->out); free(a); return NULL;
}
acs_chan_t* acs_timer_new(int period_ms, int repeat){
    pthread_t t; acs_chan_t* ch=acs_chan_new(8);
    struct timer_args* a=(struct timer_args*)malloc(sizeof(*a));
    a->out=ch; a->period_ms=period_ms; a->repeat=repeat;
    pthread_create(&t,NULL,timer_thread,a); pthread_detach(t); return ch;
}
void acs_sleep_ms(int ms){
    struct timespec ts={ ms/1000, (ms%1000)*1000000L }; nanosleep(&ts,NULL);
}

int acs_spawn(void* (*fn)(void*), void* arg){
    pthread_t t; return pthread_create(&t, NULL, fn, arg);
}
