typedef uint64_t (*alias_fn)(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_rd_a(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_rd_w(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_rd_acc(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_a_w(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_acc_a(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_acc_w(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_all_a(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_rd_zero(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_all_zero(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_rd_separate(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_a_zero(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_w_zero(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_ss_acc_zero(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_rd_a(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_rd_w(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_rd_acc(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_a_w(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_acc_a(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_acc_w(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_all_a(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_rd_zero(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_all_zero(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_rd_separate(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_a_zero(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_w_zero(uint64_t,uint64_t,uint64_t);
extern uint64_t alias_us_acc_zero(uint64_t,uint64_t,uint64_t);
static const alias_fn alias_functions[2][ALIAS_CASE_COUNT] = {
    {alias_ss_rd_a, alias_ss_rd_w, alias_ss_rd_acc, alias_ss_a_w, alias_ss_acc_a, alias_ss_acc_w, alias_ss_all_a, alias_ss_rd_zero, alias_ss_all_zero, alias_ss_rd_separate, alias_ss_a_zero, alias_ss_w_zero, alias_ss_acc_zero},
    {alias_us_rd_a, alias_us_rd_w, alias_us_rd_acc, alias_us_a_w, alias_us_acc_a, alias_us_acc_w, alias_us_all_a, alias_us_rd_zero, alias_us_all_zero, alias_us_rd_separate, alias_us_a_zero, alias_us_w_zero, alias_us_acc_zero},
};
