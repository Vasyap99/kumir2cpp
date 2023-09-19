#include "units/K_fajly.h"
#include <string>
#include <iostream>

using namespace std;

struct K_k0{
protected:
    char K_p;
    char K_nesk_lek;
public:
    void K_kkok();
    void K_nesk_leks();
};
struct K_k1 : K_k0{
    int K_d;
    K_k1(int K_c);
    virtual void K_met1();
    char K_met2(float K_a);
    bool K_met2(string K_s);
    char K_met2(char K_s,int K_e);
    char K_met2();
    void K_met3(char& K_s,int K_e);
    virtual void K_met4(K_k0* K_o,string K_l);
private:
    bool K_l;
};
void K_test1();
int K_test2();
void K_f2(int K_a,int K_b,int K_s,string& K_r,int& K_c);
string K_test3();
void K_fun(string K_s);
void K_fun(float K_v);
void K_fun();

int K_d;
void K_k0::K_kkok(){
}
void K_k0::K_nesk_leks(){
    cout << string("тест нл");
    pfile_u* K_f;
    K_f=K_otkryt____na___ctenie(string("LICENSE.txt"));
}
char K_k1::K_met2(char K_s,int K_e){
    char _result;
    _result='5';
    return _result;
}
void K_k1::K_met4(K_k0* K_o,string K_l){
    K_k0* K_kk0;
    K_kk0=this;
    cout << this->K_d << endl;
}
K_k1::K_k1(int K_c){
}
void K_k1::K_met1(){
}
char K_k1::K_met2(float K_a){
    char _result;
    _result='5';
    return _result;
}
bool K_k1::K_met2(string K_s){
    bool _result;
    _result=true;
    return _result;
}
char K_k1::K_met2(){
    char _result;
    return _result;
}
void K_k1::K_met3(char& K_s,int K_e){
    bool K_l;
}
void K_test1(){
    int K_v;
}
int K_test2(){
    int _result;
    int K_vv1;
    for(K_vv1=1;K_vv1<=10;K_vv1++){
        45;
        while(false){
        }
    }
    _result=-6;
    return _result;
}
void K_f2(int K_a,int K_b,int K_s,string& K_r,int& K_c){
    if(true){
        2+1;
        if(true){
            cout << K_a << endl;
        }else if(false){
            K_test3();
        }else{
            cout << string("выбор-иначе");
            K_r=string("стр");
        }
    }else{
        string("");
        5+8+2;
        while(true){
            if(true){
                break;
            }
        }
    }
}
string K_test3(){
    string _result;
    while(true){
        K_d=K_d+2;
        if(true) break;
    };
    _result='о';
    return _result;
}
void K_fun(string K_s){
}
void K_fun(float K_v){
}
void K_fun(){
}

int main(){
;
    for(int _temp_i0k1=0;_temp_i0k1<5;_temp_i0k1++){
        cout << string("привет") << endl;
    }
    K_k1* K_k;
    K_k1* K_k2;
    K_k=new K_k1(4);
    K_k->K_nesk_leks();
    K_k->K_met2(4.5);
    K_k->K_met2(string(1,'п'));
    K_k->K_met2('п',7);
    K_k->K_met2();
    K_k->K_met2(4);
    K_k->K_met4(K_k,string(1,'н'));
    char K_si;
    K_k->K_met3(K_si,6);
    int K_a;
    K_a=6;
    if(6*-K_a>=10 && (string(1,'в')<=string("ввод")) && K_k==K_k2 || (K_k!=K_k2) || (K_k->K_d|5)>0 || !(100==(~(K_d)))){
        cout << true << endl;
    }
    2+2;
    string K_r;
    cout << K_a << K_test3() << endl;
    cin >> K_a >> K_r;
    K_k->K_met1();
    delete K_k;
    K_fun(string(1,'о'));
    K_fun(7);
    K_fun();
    return 0;
}
