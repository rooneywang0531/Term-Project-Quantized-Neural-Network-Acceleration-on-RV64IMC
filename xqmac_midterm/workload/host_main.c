#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "model_data.h"
int model_run(const int8_t *,const int8_t *);
const int8_t *model_output(void);
int main(int argc,char **argv)
{
    if(argc!=2){fprintf(stderr,"usage: host_model fixtures/random.bin\n");return 99;}
    FILE *f=fopen(argv[1],"rb");if(!f){perror(argv[1]);return 99;}
    int8_t *fixture=malloc(INPUT_BYTES+GOLDEN_BYTES);
    if(!fixture){fclose(f);return 99;}
    if(fread(fixture,1,INPUT_BYTES+GOLDEN_BYTES,f)!=INPUT_BYTES+GOLDEN_BYTES || fgetc(f)!=EOF){fprintf(stderr,"bad fixture length\n");fclose(f);free(fixture);return 99;}
    fclose(f);int result=model_run(fixture,fixture+INPUT_BYTES);
    if(!result){const int8_t *p=model_output();int top=0;for(int i=1;i<1000;++i)if(p[i]>p[top])top=i;
#ifdef SCOPE_BLOCK
    printf("PASS block: 3 operators, 200704 outputs per stage.\n");
    (void)top;
#else
    printf("PASS full model: 37 operators, 1000 final logits; top1 index=%d (synthetic input).\n",top);
#endif
}
    free(fixture);return result;
}
