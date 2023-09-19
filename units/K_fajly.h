#include "pfile.h"
#include <string>

using namespace std;

pfile_u* K_otkryt____na___ctenie(string K_im_ja);
pfile_u* K_otkryt____na_zapis___(string K_im_ja);

pfile_u* K_otkryt____na___ctenie(string K_im_ja){
        pfile_u* _result;
    pfile_u* K_f;
    K_f=new pfile_u;
    K_f->assign(K_im_ja);
    K_f->reset();
    _result=K_f;
    return _result;
}
pfile_u* K_otkryt____na_zapis___(string K_im_ja){
    pfile_u* _result;
    pfile_u* K_f;
    K_f=new pfile_u;
    K_f->assign(K_im_ja);
    K_f->rewrite();
    _result=K_f;
    return _result;
}

