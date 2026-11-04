#include <cstdint>
#include "extension.h"
#include "xqmac_semantics.h"
#include "rq_semantics.h"

static reg_t execute_qmac(processor_t *p,insn_t insn,reg_t pc,bool us,bool logged)
{
    if(p->get_xlen()!=64)throw trap_illegal_instruction(insn.bits());
    // Capture ALL old sources first: correct even when rd aliases any source.
    const reg_t a=p->get_state()->XPR[insn.rs1()];
    const reg_t w=p->get_state()->XPR[insn.rs2()];
    const reg_t acc=p->get_state()->XPR[insn.rs3()];
    const reg_t value=xqmac_ref(a,w,acc,us);
    if(logged)p->get_state()->log_reg_write[insn.rd()<<4]={value,0};
    p->get_state()->XPR.write(insn.rd(),value); // x0 write is discarded.
    return pc+4;
}
static reg_t ss_fast(processor_t *p,insn_t i,reg_t pc){return execute_qmac(p,i,pc,false,false);}
static reg_t us_fast(processor_t *p,insn_t i,reg_t pc){return execute_qmac(p,i,pc,true,false);}
static reg_t ss_logged(processor_t *p,insn_t i,reg_t pc){return execute_qmac(p,i,pc,false,true);}
static reg_t us_logged(processor_t *p,insn_t i,reg_t pc){return execute_qmac(p,i,pc,true,true);}
static reg_t execute_rq(processor_t *p,insn_t insn,reg_t pc,bool logged,bool single=false)
{
    if(p->get_xlen()!=64)throw trap_illegal_instruction(insn.bits());
    const reg_t x=p->get_state()->XPR[insn.rs1()];
    const reg_t m=p->get_state()->XPR[insn.rs2()];
    const reg_t r=p->get_state()->XPR[insn.rs3()];
    if(!(single?sr_valid(m,r):rq_valid(m,r)))throw trap_illegal_instruction(insn.bits());
    const reg_t value=single?sr_ref(x,m,r):rq_ref(x,m,r);
    if(logged)p->get_state()->log_reg_write[insn.rd()<<4]={value,0};
    p->get_state()->XPR.write(insn.rd(),value);
    return pc+4;
}
static reg_t rq_fast(processor_t *p,insn_t i,reg_t pc){return execute_rq(p,i,pc,false);}
static reg_t rq_logged(processor_t *p,insn_t i,reg_t pc){return execute_rq(p,i,pc,true);}
static reg_t sr_fast(processor_t *p,insn_t i,reg_t pc){return execute_rq(p,i,pc,false,true);}
static reg_t sr_logged(processor_t *p,insn_t i,reg_t pc){return execute_rq(p,i,pc,true,true);}
static reg_t unavailable(processor_t *,insn_t i,reg_t){throw trap_illegal_instruction(i.bits());}

struct register_arg_t:arg_t{
    unsigned field;
    explicit register_arg_t(unsigned f):field(f){}
    std::string to_string(insn_t i)const override{
        unsigned r=field==0?i.rd():field==1?i.rs1():field==2?i.rs2():i.rs3();
        return xpr_name[r];
    }
};
static register_arg_t arg_rd(0),arg_a(1),arg_w(2),arg_acc(3);
class xqmac_t:public extension_t{
public:
    const char *name()const override{return "xqmac";}
    // Generated against the user's own matching Spike headers.
    #include "spike_adapter.inc"
};
REGISTER_EXTENSION(xqmac, [](){return new xqmac_t;})
