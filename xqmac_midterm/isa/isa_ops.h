#ifndef ISA_OPS_H
#define ISA_OPS_H
#include <stdint.h>
#ifdef XQMAC_EMULATE
#include "xqmac_semantics.h"
#include "rq_semantics.h"
#define QMAC_SS(a,w,c) xqmac_ref((a),(w),(c),0)
#define QMAC_US(a,w,c) xqmac_ref((a),(w),(c),1)
#define RQ_DR(x,m,r) ((int32_t)rq_ref((uint64_t)(int64_t)(x),(m),(r)))
#define RQ_SR(x,m,r) ((int32_t)sr_ref((uint64_t)(int64_t)(x),(m),(r)))
#else
#include "xqmac.h"
#include "xqrequant.h"
#define QMAC_SS(a,w,c) xqmac4_ss_raw((a),(w),(c))
#define QMAC_US(a,w,c) xqmac4_us_raw((a),(w),(c))
#define RQ_DR(x,m,r) xqrequant_dr((x),(m),(r))
#define RQ_SR(x,m,r) xqrequant_sr((x),(m),(r))
#endif
#endif
