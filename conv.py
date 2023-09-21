#coding:cp1251

import sys
import pickle #��� ���������� ������ �������

if len(sys.argv)<2:
    print 'kumir to c++11 converter'
    print 'usage: conv.py <file.kum>'
    print ' or to translate as module:'
    print 'usage: conv.py <file.kum> -m'
    sys.exit()

interface_mode=False

UNITS=[]  #������ ����� ������������ h-������ �� �������
UNIT_HAS_INIT_SECT=False
UNITS_INIT_PROCS=[]  #������ ���� �������� ������������� ������������ �������

PREFIX=''  #��� ����������� � ����� ������������ ������� � ������(����� �� ���� ��������� ���� � ����������)

IDENT_REPLACE={'chr':'���','ord':'���','(.':'[','.)':']'}     #������ ��������������� ��� ������������� ���� � c++
repl=IDENT_REPLACE

#��� �������� ��������� ��� �������������� �����: 
BASICTYPES={'���','���','���','���','���','���'}

def typeconv(t):
    try:
        return TYPECONV[t]
    except:
        return t
#

PNAME=""  #��� ��������� ��� ����������

def detect_cyr(s):
    cyr=False
    for i in s:
        if ord(i)>=ord('�') and ord(i)<=ord('�') or ord(i)>=ord('�') and ord(i)<=ord('�'):
            cyr=True
            return cyr
    return cyr
def perform_cyr0(s):
    nm="K_"
    d={"�":"j", "�":"c", "�":"u", '�':'k' ,'�':'e' ,'�':'n' ,'�':'g' ,'�':'__s' ,'�':'__sh' ,'�':'z' ,'�':'h' ,'�':'_I' ,'�':'f' ,'�':'y' ,'�':'v' ,'�':'a' ,'�':'p' ,'�':'r' ,'�':'o' ,'�':'l' ,'�':'d' ,'�':'__z' ,'�':'__e' ,'�':'_ja' ,'�':'__c' ,'�':'s' ,'�':'m' ,'�':'i' ,'�':'t' ,'�':'___' ,'�':'b' ,'�':'_ju'
        ,
       "�":"j", "�":"c", "�":"u", '�':'k' ,'�':'e' ,'�':'n' ,'�':'g' ,'�':'__s' ,'�':'__sh' ,'�':'z' ,'�':'h' ,'�':'_I' ,'�':'f' ,'�':'y' ,'�':'v' ,'�':'a' ,'�':'p' ,'�':'r' ,'�':'o' ,'�':'l' ,'�':'d' ,'�':'__z' ,'�':'__e' ,'�':'_ja' ,'�':'__c' ,'�':'s' ,'�':'m' ,'�':'i' ,'�':'t' ,'�':'___' ,'�':'b' ,'�':'_ju'
      }
    for i in s:
        if i in d.keys():
            nm+=d[i]
        else:
            nm+=i
    return nm
def perform_cyr(s):
    s1=ident_repl(s)
    #print '=======',s1
    #raw_input() 
    return perform_cyr0(s1) if detect_cyr(s1) else s1
def perform_cyr_l(l):
    return "".join([perform_cyr(i) for i in l])
#=================================================================
class cpp_code_generator:
    def __init__(self,nm="out.cpp"):
        global PNAME
        self.N1=nm.split('.')
        PNAME=self.N1[0]
        self.typ=1  if '-m' in sys.argv else  0  #0-program,1-unit
        self.f=None
        self.ext="cpp"  if self.typ==0 else  "h"

        self.class_headers=""  #��������� �������
        self.headers=""  #��������� ��������-��� �������� �������(��������� ��� kumir)

        self.body_prefix=""   #������, ������������ � ��������� � ����� ������(������,define,using)
        self.body_globals=""  #�������, ����.�����, ����
        self.body=[""]        #��� ���� ����(begin-end)

        self.fbodies=[]       #��� ��������
        self.curr_code=self.body
        self.level=0                #������� ����������� �������(0=���������� ���������)

        self.func_par_list="" 

        self.string_inluded=False
        self.null_inluded=False
        self.iostream_inluded=False
        self.cstdlib_inluded=False
        self.pfile_inluded=False
        self.stdexcept_inluded=False

        self.expr="" 

        self.OTSTUP=0

        self.nado=""
    def nado_b(self):
        self.nado=""
    def nado_e(self):
        self.curr_code[0]+=self.nado
        self.nado=""
    def split_type_s(self,s):
        if s[-1]=='*':
            return [s[:-1],s[-1]]
        else:
            return [s] 
    def init_file(self): #������������� ��������� �����
        self.f=open(perform_cyr(self.N1[0])+'.'+self.ext,"wb")

    def expr1(self):
        self.expr=""

    def ADD(self,s):
        self.curr_code[0]+="    " * self.OTSTUP + s
    def incl_string(self):
        if not self.string_inluded:
            self.body_prefix+='#include <string>\r\n'
            self.string_inluded=True
    def incl_null(self):
        if not self.null_inluded:
            self.body_prefix+='#define null 0\r\n'
            self.null_inluded=True
    def incl_iostream(self):
        if not self.iostream_inluded:
            self.body_prefix+='#include <iostream>\r\n'
            self.iostream_inluded=True
    def incl_cstdlib(self):
        if not self.cstdlib_inluded:
            self.body_prefix+='#include <cstdlib>\r\n'
            self.cstdlib_inluded=True
    def incl_stdexcept(self):
        if not self.stdexcept_inluded:
            self.body_prefix+='#include <stdexcept>\r\n'
            self.stdexcept_inluded=True
    def incl_pfile(self):
        if not self.pfile_inluded:
            self.body_prefix+='#include "pfile.h"\r\n'
            self.pfile_inluded=True


    def func1header(self,fname,ftype,level=0,class_name=''):
        #
        #if level>self.level:
        #    self.fbodies.append([""])
        #    self.curr_code=self.fbodies[-1]  
        #self.level=level
        #
        try:  #������� ������� � �����
            if self.func_par_list[-1]==',':
                self.func_par_list=self.func_par_list[:-1]
        except:
            pass
        if class_name=='':
            self.headers += perform_cyr_l(self.split_type_s(ftype))+' '+perform_cyr(fname)+'('+self.func_par_list+')'+';'+'\r\n'

    def func1(self,fname,ftype,level=0,class_name=''):
        #
        if level>self.level:
            self.fbodies.append([""])
            self.curr_code=self.fbodies[-1]  
        self.level=level
        #
        try:  #������� ������� � �����
            if self.func_par_list[-1]==',':
                self.func_par_list=self.func_par_list[:-1]
        except:
            pass
        if class_name=='':
            self.curr_code[0] += perform_cyr_l(self.split_type_s(ftype))+' '+perform_cyr(fname)+'('+self.func_par_list+')'+'{'+'\r\n'
        elif fname=='�����������':   #��� �����������
            self.curr_code[0] += perform_cyr(class_name)+'::'+perform_cyr(class_name)+'('+self.func_par_list+')'+'{'+'\r\n'
        else:
            self.curr_code[0] += perform_cyr_l(self.split_type_s(ftype))+' '+perform_cyr(class_name)+'::'+perform_cyr(fname)+'('+self.func_par_list+')'+'{'+'\r\n'
        self.OTSTUP+=1
        self.ADD( '    '+self.perform_type(ftype,'_result')+';\r\n' )   #��������� ���������� ��� ���������� �-���
    def func2(self):
        self.ADD( '    return _result;\r\n' )
        self.OTSTUP-=1
        self.curr_code[0] += '}\r\n'
        self.level-=1

    def proc1header(self,fname,level=0,class_name=''):
        #
        #if level>self.level:
        #    self.fbodies.append([""])
        #    self.curr_code=self.fbodies[-1]  
        #self.level=level
        #
        try:  #������� ������� � �����
            if self.func_par_list[-1]==',':
                self.func_par_list=self.func_par_list[:-1]
        except:
            pass
        if class_name=='':
            self.headers += 'void '+perform_cyr(fname)+'('+self.func_par_list+')'+';'+'\r\n'
        #self.OTSTUP+=1
    def proc1(self,fname,level=0,class_name=''):
        #
        if level>self.level:
            self.fbodies.append([""])
            self.curr_code=self.fbodies[-1]  
        self.level=level
        #
        try:  #������� ������� � �����
            if self.func_par_list[-1]==',':
                self.func_par_list=self.func_par_list[:-1]
        except:
            pass
        if class_name=='':
            self.curr_code[0] += 'void '+perform_cyr(fname)+'('+self.func_par_list+')'+'{'+'\r\n'
        elif fname=='�����������':   #��� �����������
            self.curr_code[0] += perform_cyr(class_name)+'::'+perform_cyr(class_name)+'('+self.func_par_list+')'+'{'+'\r\n'
        else:
            self.curr_code[0] += 'void'+' '+perform_cyr(class_name)+'::'+perform_cyr(fname)+'('+self.func_par_list+')'+'{'+'\r\n'
        self.OTSTUP+=1
    def proc2(self):
        self.OTSTUP-=1
        self.curr_code[0] += '}\r\n'
        self.level-=1
    def dump(self):
        if len(self.fbodies)>0:
            self.body_globals+=self.fbodies.pop()[0]
            try:
                self.curr_code=self.fbodies[-1]
            except:
                self.curr_code=self.body 
    def dump_header(self):  #��� ���������� ��������/�-��� � �������
        if len(self.fbodies)>0:
            self.fbodies.pop()[0]
            try:
                self.curr_code=self.fbodies[-1]
            except:
                self.curr_code=self.body 

    def dumpg(self):
        global UNITS, UNIT_HAS_INIT_SECT, PNAME 
        for i in UNITS:            #��������� � ������������ ��� ��� ������������ h-�����
            self.f.write(i+'\r\n')

        self.f.write(self.body_prefix)
        self.f.write("\r\n")
        if self.string_inluded or self.null_inluded or self.iostream_inluded or self.cstdlib_inluded or self.pfile_inluded:
            self.f.write("using namespace std;")
            self.f.write("\r\n")

        self.f.write("\r\n")
        self.f.write(self.class_headers)  #��������� ��� kumir
        self.f.write(self.headers)  #��������� ��� kumir

        self.f.write("\r\n")
        self.f.write(self.body_globals)

        self.f.write("\r\n")
        if self.typ==0:                        #program type=0program
            self.f.write("int main(){\r\n")
            for i in UNITS_INIT_PROCS:
                self.f.write("    "+i+"();\r\n")
            self.f.write(self.body[0])
            self.f.write("    return 0;\r\n")
            self.f.write("}\r\n")
        if self.typ==1 and UNIT_HAS_INIT_SECT: #program type=1unit
            self.f.write("void _"+PNAME+"_init(){\r\n")
            self.f.write(self.body[0])
            self.f.write("}\r\n")

    def o_func_zag(self,fname,ftype,dt,virtual=False,cname=''): #��������� �-��� ������ ���������� ������
        global interface_mode
        if interface_mode:
            return
        try:  #������� ������� � �����
            if self.func_par_list[-1]==',':
                self.func_par_list=self.func_par_list[:-1]
        except:
            pass
        dt[0] += '    '
        if virtual:
            dt[0] += 'virtual '
        if fname=='�����������':   #��� �����������
            dt[0] += perform_cyr(cname)+'('+self.func_par_list+')'+';'+'\r\n'
        else:
            dt[0] += perform_cyr_l(self.split_type_s(ftype))+' '+perform_cyr(fname)+'('+self.func_par_list+')'+';'+'\r\n'


    def while1(self):
        try:
            if self.curr_code[0][-3] in {';','{','}'}:
                self.ADD("while(")
            else:
                self.curr_code[0]=self.curr_code[0][:-2]+' '+"while("                
        except:
            self.ADD("while(")
    def while2(self):
        self.curr_code[0]+=")"
    def while_true(self):
        try:
            if self.curr_code[0][-3] in {';','{','}'}:
                self.ADD("while(true)")
            else:
                self.curr_code[0]=self.curr_code[0][:-2]+' '+"while(true)"                
        except:
            self.ADD("while(true)")
    def utv1(self):
        self.incl_stdexcept()
        self.ADD("    if(!(")
    def utv2(self):
        self.curr_code[0]+=')) throw std::invalid_argument("");\r\n'
    def if1(self):
        try:
            if self.curr_code[0][-3] in {';','{','}'}:
                self.ADD("if(")
            else:
                self.curr_code[0]=self.curr_code[0][:-2]+' '+"if("                
        except:
            self.ADD("if(")
    def if2(self):
        self.curr_code[0]+=")"
    def if_else(self):
        try:
            if self.curr_code[0][-3]=='}':
                self.curr_code[0]=self.curr_code[0][:-2]+"else\r\n"
            else:
                self.ADD("else\r\n")
        except:
            self.ADD("else\r\n")
    def end_operator_semicolon(self):
        if self.curr_code[0][-3:] not in{';\r\n','}\r\n'}:
            self.curr_code[0]+=";\r\n"
    def gblock_begin(self):
        print "---BLOCK_B"
        #self.curr_code[0]+="{\r\n"
        self.OTSTUP+=1
        self.level+=1
    def gblock_end(self):
        print "---BLOCK_E"
        self.OTSTUP-=1
        #self.ADD("}\r\n")
        self.level-=1

    def block_begin(self):
        print "---BLOCK_B"
        if self.curr_code[0][-6:-2] in {'else'} and self.curr_code[0][-2:]=='\r\n':
            self.curr_code[0]=self.curr_code[0][:-2]+"{\r\n"
        else:
            self.curr_code[0]+="{\r\n"
        #self.OTSTUP+=1
    def block_end(self):
        print "---BLOCK_E"
        #self.OTSTUP-=1
        self.ADD("}\r\n")

    def expr2(self,IDENT,IDENT_TYPE):
        def filterL(lex):
            if lex==':=':
                return '='
            elif lex=='=':
                return '=='
            elif lex=='<>':
                return '!='
            elif lex=='�����':
                GEN.incl_NULL()
                return 'null'
            elif lex=='�':
                return ' && '
            elif lex=='���':
                return ' || '
            elif lex=='����':
                return ' ^ '
            elif lex=='��':
                return '!'
            elif lex=='��':
                return 'true'
            elif lex=='���':
                return 'false'
            elif lex=='���':
                return 'this'
            elif lex=='shl':
                return '<<'
            elif lex=='shr':
                return '>>'
            elif lex=='@':
                return '&'
            elif lex=='^':
                return '*'
            else:
                return lex 
        if IDENT_TYPE=='iden':
            self.expr+=perform_cyr(IDENT)
        elif IDENT_TYPE=='char':
            self.expr+="'"+IDENT+"'"
        elif IDENT_TYPE=='stra':
            self.expr+='string("'+IDENT+'")'
        else:
            self.expr+=filterL(IDENT)
    def expr3(self):
        self.curr_code[0]+=self.expr

    def for1(self,FOR_ID):
        try:
            if self.curr_code[0][-3] in {';','{','}'}:
                self.ADD("for("+perform_cyr(FOR_ID)+'=')
            else:
                self.curr_code[0]=self.curr_code[0][:-2]+' '+"for("+perform_cyr(FOR_ID)+'='                
        except:
            self.ADD("for("+perform_cyr(FOR_ID)+'=')
    def for2(self,FOR_ID):
        self.curr_code[0]+=';'+perform_cyr(FOR_ID)+'<='
    def for3(self,FOR_ID):
        self.curr_code[0]+=';'+perform_cyr(FOR_ID)+'++)'

    def repeat(self):
        try:
            if self.curr_code[0][-3] in {';','{','}'}:
                self.ADD("do{\r\n")
            else:
                self.curr_code[0]=self.curr_code[0][:-2]+' '+"do{\r\n"                
        except:
            self.ADD("do{\r\n")
        self.OTSTUP+=1
    def until1(self):
        self.OTSTUP-=1
        self.ADD('}while(!( ')
    def until2(self):
        self.curr_code[0]+=' ))'

    def perform_type(self,tp,var_nm):  #��������������� ������� ��� �������������� ���� (��� �����������(���������� � ���������� c++ �����������))
                                       #����������� ������ � �����, ���� ����.������������ �� ����������
        def fix_array(s):   #
            i=len(s)-1
            while s[i]==']':
                i-=1
                while s[i] in {'0','1','2','3','4','5','6','7','8','9'}:
                    i-=1
                i-=1
            return i 
        s=tp[:]
        if s[-1]==']':
            i=fix_array(s)
            return perform_cyr(s[:i+1])+' '+var_nm+s[i+1:]
        return perform_cyr_l(self.split_type_s(s))+' '+var_nm        

    def var(self,vars,tp):
        for i in vars:
            if self.level>0:
                self.ADD(self.perform_type(tp,perform_cyr(i))+';\r\n')
            else:
                self.body_globals += self.perform_type(tp,perform_cyr(i))+';\r\n'

    def TYPE(self,type_n,tp):
        self.body_globals += 'typedef '+self.perform_type(tp,type_n)+';\r\n'


    def struct1(self,record_num,dt,parents=[],T_NAME=""):  #dt=[str()] - ����� ��� ������ ������� (����� ������� �� ������������� ��� ������ � body_globals)
        global interface_mode
        if interface_mode:
            return
        global PREFIX
        if len(parents)==0:
            dt[0] += 'struct '+perform_cyr(T_NAME)+'{\r\n'
        else:
            dt[0] += 'struct '+perform_cyr(T_NAME)+' : '+','.join([perform_cyr(i) for i in parents])+'{\r\n'
    def struct2(self,dt):
        global interface_mode
        if interface_mode:
            return
        dt[0] += '};\r\n'
        self.class_headers += dt[0]
    def object_data_entry(self,vars,tp,dt):
        global interface_mode
        if interface_mode:
            return
        for i in vars:
            dt[0] += '    '+self.perform_type(tp,perform_cyr(i))+';\r\n'

    def par_list1(self):
        self.func_par_list=""
    def par_list_var_entry(self,vars,tp):
        for i in vars:
            self.func_par_list+=self.perform_type(tp+'&',perform_cyr(i))+','
    def par_list_entry(self,vars,tp):
        for i in vars:
            self.func_par_list+=self.perform_type(tp,perform_cyr(i))+','

    def uses(self,units):
        global UNITS
        for i in units:
            if i not in UNITS:
                UNITS.append('#include'+' "units/'+i+'.h"')
            #self.body_prefix+='#include'+' "units/'+i+'.h"\r\n'
            

    def write1(self):
        self.ADD('cout')
    def write2(self):
        self.curr_code[0]+=' << '
    def write3(self):
        pass
    def read1(self):
        self.ADD('cin')
    def read2(self):
        self.curr_code[0]+=' >> '
    def read3(self):
        pass
    def writeln(self):
        self.curr_code[0]+=' << endl'


GEN=cpp_code_generator(sys.argv[1])
#===========================================================================
#====================================== ���� ��������������� ������� ===========================================
def ERR(s):
    print 'ERROR! '+s
    raw_input("press Ctrl+C")
def P(s):
    print s

VYRKONSET={'����','����',';','���','��','�����','���','���','����','�����','����','��','�����','���',':'} #��������� ������ ��� ����������� ����� ���������

class sint_anal:
    def __init__(self,LEXEMS,GEN):
        #global LEXEMS,GEN
        self.LEX=LEXEMS
        self.GEN=GEN
        self.i=0 #������� ������
        self.L=[] 
        self.LEVEL=0  #������� ����������� �������(0=���������� �������) 
        self.var_list=[]  #������ ���� ���������� � ������ ���������� � ������ var

        self.record_num=0  #������� ������������ ��������������� ����� struct � ������������ ���� cpp
        self.record_num1=0  #������� ������������ ��������������� �����������(dcl)��� ��������� ����� struct
        self.decls=[[]]  #   [     [each proc:  ['t/v/c','name','categ(1-v/2-p/3-f)',[type_lex_list],(extra) <,object decls> ]  ]     ]
        #self.with_decls=[]  #�� �� �����, ��� decls, ������ ��� ���������� with
        #self.with_expr=[] #���� ��������������� ���� ��������� ��� with
        #
        self.last_acs_modifier='���'
        self.inner_decls=[]  #��� ������ ������(��� ������ ������ ������� � 1 ������ � ������� �������� ���-�)
        #
        self.class_name1="" #��� ��� �-���(����� ������������ this)
        #
        self.temp_var_n=0 #������� ��������������� ���������� (��� ��������� ������  �� N ���)
        #*
        self.TRmethod_buf="" #* (����� ���� ������� �� ������)��� �������� ������� �� ������� ������ ��� 0�� �������
        self.TRclass_name="" #* (��� ������)��� �������� ������� �� ������� ������ ��� 0�� �������

    def cat_lex(self): #���������� ��������� ������ ������� ���������������,������� � ��������,� 1
                       #(��� ��������� ��������������� �� ���������� ����)
        if self.LEX[self.i][1]!='iden':
            return  
        i=self.i+1        
        while self.LEX[i][1]=='iden':
            self.LEX[self.i][0]+='_'+self.LEX[i][0]
            i+=1  
        self.LEX=self.LEX[:self.i+1]+self.LEX[i:]  #�������� �� ������ �������������� �������
    def calc_type_bin(self,d1,d2,op): #���������� ���� � �������� ���������
        ops_t={
          ('���','���','+'):('���'),
          ('���','���','-'):('���'),
          ('���','���','*'):('���'),
          ('���','���','/'):('���'),
          ('���','���','+'):('���'),
          ('���','���','-'):('���'),
          ('���','���','*'):('���'),
          ('���','���','/'):('���'),
          ('���','���','+'):('���'),
          ('���','���','-'):('���'),
          ('���','���','*'):('���'),
          ('���','���','/'):('���'),
          ('���','���','+'):('���'),
          ('���','���','-'):('���'),
          ('���','���','*'):('���'),
          ('���','���','/'):('���'),

          ('���','���','+'):('���'),
          ('���','���','+'):('���'),
          ('���','���','+'):('���'),
          ('���','���','+'):('���'),

          ('���','���','�'):('���'),
          ('���','���','���'):('���'),
          ('���','���','����'):('���'),

          ('���','���','�'):('���'),             #��������� �������� � ������
          ('���','���','���'):('���'),
          ('���','���','����'):('���'),

          ('���','���','='):('���'),
          ('���','���','<>'):('���'),
          ('���','���','>'):('���'),
          ('���','���','<'):('���'),
          ('���','���','>='):('���'),
          ('���','���','<='):('���'),

          ('���','���','='):('���'),
          ('���','���','<>'):('���'),
          ('���','���','>'):('���'),
          ('���','���','<'):('���'),
          ('���','���','>='):('���'),
          ('���','���','<='):('���'),

          ('���','���','>'):('���'),
          ('���','���','<'):('���'),
          ('���','���','>='):('���'),
          ('���','���','<='):('���'),

          ('���','���','>'):('���'),
          ('���','���','<'):('���'),
          ('���','���','>='):('���'),
          ('���','���','<='):('���'),

          ('���','���','='):('���'),
          ('���','���','<>'):('���'),
          ('���','���','>'):('���'),
          ('���','���','<'):('���'),
          ('���','���','>='):('���'),
          ('���','���','<='):('���'),

          ('���','���','='):('���'),
          ('���','���','<>'):('���'),
          ('���','���','>'):('���'),
          ('���','���','<'):('���'),
          ('���','���','>='):('���'),
          ('���','���','<='):('���'),

          ('���','���','='):('���'),
          ('���','���','<>'):('���'),
          ('���','���','>'):('���'),
          ('���','���','<'):('���'),
          ('���','���','>='):('���'),
          ('���','���','<='):('���'),

          ('���','���','='):('���'),
          ('���','���','<>'):('���'),
          ('���','���','>'):('���'),
          ('���','���','<'):('���'),
          ('���','���','>='):('���'),
          ('���','���','<='):('���'),

          ('���','���','='):('���'),
          ('���','���','<>'):('���'),
          ('���','���','>'):('���'),
          ('���','���','<'):('���'),
          ('���','���','>='):('���'),
          ('���','���','<='):('���'),
        }
        try:
            ttl=ops_t[(d1[3][0],d2[3][0],op)]
        except:
            ttl=('���')  #���� ����� ��� � ������, �� ��� ��������� ��������, ����� ��� ��������� ���������� � ��������� ����������
        return ['c','','1',ttl,(),None]

    def create_record_decl_list(self,dcl): #(�������)
        return dcl   
    #
    def check(self,s,msg):
        if self.LEX[self.i][0]==s: 
            self.i+=1
        else:
            ERR(msg) 

    def rule_sym(self,s):
        P("rule_sym:"+unicode(s,"cp1251"))
        self.check(s,"symbol '"+unicode(self.LEX[self.i][0],'cp1251')+"'")

    def rule_ident(self):
        P("rule_ident: "+self.LEX[self.i][0])
        self.IDENT=self.LEX[self.i][0][:]
        self.IDENT_TYPE=self.LEX[self.i][1][:]
        self.i+=1
    def find_id_decl(self,id):  #����� ���������� ���� ���� � ������������
        for i in reversed(self.decls):
            for j in reversed(i):
                if j[1]==id:  #����� ���������� ���� �-��� ���� ���
                    return j
        raise BaseException("ERR:id declaration not found! ("+id+') '+str(self.decls))
    def find_id_decl_list(self,id,dcl_l):  #����� ������ decl-�� ��� ����� (��� ���������� ������� � ������� ��� �-��� �� ������� � 1 �������)
        L=[]
        for i in reversed(dcl_l):
            for j in reversed(i):
                if j[1]==id:  #����� ���������� ���� �-��� ���� ���
                    L.append(j[:])
        return L
        raise BaseException("ERR:id declaration not found! ("+id+') '+str(self.decls))

    def resolve_type(self,dcl):  #������� ����������� ����, ���� �� �� �������  (�������� ����������� ��� ��������� ���)
        if dcl[3][0] not in {'','���','���','���','���','���','���'}:
            return self.find_id_decl(dcl[3][0])[:]
        else:
            return dcl 

    def rule_expr(self): #���������, � ��� �����, �� ������ ������������
        P(">rule_expr")
        self.GEN.expr1()
        TYP=self.rule_expr0()
        self.GEN.expr3()
        P('<')
        return TYP

    def rule_expr0(self):#0� ������� ��������� - �������� �������� �� ������� :=
        P(">rule_expr0")        
        SGN=''
        while True:
            TYP=self.rule_expr1()
            if self.LEX[self.i][0] in{':=','-=','+=','*=','/='} and not(  (self.LEX[self.i][0] in VYRKONSET) and (self.LEX[self.i][1] in {'swrd','sign'})  ):
                self.rule_ident() #���������� ����
                SGN=self.IDENT
                self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
                TYP=['c','','1',[''],[]]
            else:
                break
        P('<0 '+SGN+' '+self.LEX[self.i][0])
        return TYP

    def rule_expr1(self):#1� ������� ��������� - �������� ���������� ��������( or )
        P(">rule_expr1")        
        TYP=['v','',1,[''],[]]
        OP=""
        while True:
            TYP1=self.rule_expr1_1()
            if TYP[3][0]!='':
                TYP=self.calc_type_bin(TYP,TYP1,'���')
            else:
                TYP=TYP1[:]
            if self.LEX[self.i][0] in{'���'} and not(  (self.LEX[self.i][0] in (VYRKONSET | {',',']'}) ) and (self.LEX[self.i][1] in {'swrd','sign'})  ):
                self.rule_ident() #���������� ����
                OP=self.IDENT[:]
                if TYP[3][0]=='���':
                    self.GEN.expr+='|'
                else: 
                    self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            else:
                break
        P('<1 '+str(TYP))    
        return TYP 

    def rule_expr1_1(self):#1_1� ������� ��������� - �������� ���������� ��������( and xor)
        P(">rule_expr1_1")        
        OP=''
        TYP=['v','',1,[''],[]]
        while True:
            TYP1=self.rule_expr2_1()
            if TYP[3][0]!='':
                TYP=self.calc_type_bin(TYP,TYP1,OP)
            else:
                TYP=TYP1[:]
            if self.LEX[self.i][0] in{'�','����'} and not(  (self.LEX[self.i][0] in (VYRKONSET | {',',']'}) ) and (self.LEX[self.i][1] in {'swrd','sign'})  ):
                self.rule_ident() #���������� ����
                OP=self.IDENT[:]
                if TYP[3][0]=='���':
                    if OP=='�':
                        self.GEN.expr+='&'
                    elif OP=='����':
                        self.GEN.expr+='^'
                else: 
                    self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            else:
                break
        P('<1 '+str(TYP))    
        return TYP 
         
    def rule_expr2_1(self):#2_1� ������� ��������� - ������� ���������� ��������( ��)
        P(">rule_expr2_1")        
        if self.LEX[self.i][0] in{'��'}:
            self.rule_ident() # 
            OP=self.IDENT[:]
            N=len(self.GEN.expr)
            self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            self.GEN.expr2('(','sign')
            TYP=self.rule_expr2_1()
            self.GEN.expr2(')','sign')
            if OP=='��' and TYP[3][0]=='���':   #��������� ��
                self.GEN.expr=self.GEN.expr[:N]+"~"+self.GEN.expr[N+1:]
        else:
            TYP=self.rule_expr2()
        P("<2_1")
        return TYP


    def rule_expr2(self):#2� ������� ��������� - �������� ���������� ��������( > < >= <= = <>)
        perf=False
        P(">rule_expr2")        
        OP=''
        TYP=['v','',1,[''],[]]
        while True:
            N1=len(self.GEN.expr)  #����� �������, ���� ����� ��������� ��� �������������� ����.� ���. c-> string(c)
            TYP1=self.rule_expr3()
            if TYP[3][0]!='':
                TYP=self.calc_type_bin(TYP,TYP1,OP)
            else:
                TYP=TYP1[:]
            if ((TYP1[3][0]=='���') and ((self.LEX[self.i][0] in{'>','<','>=','<=','=','<>'}) or perf)): #�������������� ����.� ���. c-> string(c)
                self.GEN.expr=self.GEN.expr[:N1]+'string(1,'+self.GEN.expr[N1:]+')'
                perf=True
            if self.LEX[self.i][0] in{'>','<','>=','<=','=','<>'} and not(  (self.LEX[self.i][0] in VYRKONSET) and (self.LEX[self.i][1] in {'swrd','sign'})  ):
                self.rule_ident() #���������� ����
                OP=self.IDENT[:]
                self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            else:
                break
        P('<2')
        return TYP 

    def rule_expr3(self):#3� ������� ��������� - �������� ��������( + -)
        perf=False
        P(">rule_expr3")      
        OP=''  
        TYP=['v','',1,[''],[]]
        while True:
            N1=len(self.GEN.expr)  #����� �������, ���� ����� ��������� ��� �������������� ����.� ���. c-> string(c)
            TYP1=self.rule_expr4()
            if TYP[3][0]!='':
                TYP=self.calc_type_bin(TYP,TYP1,OP)
            else:
                TYP=TYP1[:]
            if self.LEX[self.i][0] in{'+','-'} and not(  (self.LEX[self.i][0] in VYRKONSET) and (self.LEX[self.i][1] in {'swrd','sign'})  ):
                if self.LEX[self.i][0]=='+' and (TYP[3][0]=='���'): #�������������� ����.� ���. c-> string(c)
                    self.GEN.expr=self.GEN.expr[:N1]+'string(1,'+self.GEN.expr[N1:]+')'
                    perf=True
                self.rule_ident() #���������� ����
                OP=self.IDENT[:]
                self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            else:
                break
        P("<3")
        return TYP 

    def rule_expr4(self):#4� ������� ��������� - �������� ��������( * / shl shr div mod )
        P(">rule_expr4")        
        OP=''  
        TYP=['v','',1,[''],[]]
        while True:
            TYP1=self.rule_expr4_1()
            if TYP[3][0]!='':
                TYP=self.calc_type_bin(TYP,TYP1,OP)
            else:
                TYP=TYP1[:]
            if self.LEX[self.i][0] in{'*','/','<<','>>','div','mod'} and not(  (self.LEX[self.i][0] in VYRKONSET) and (self.LEX[self.i][1] in {'swrd','sign'})  ):
                self.rule_ident() #���������� ����
                OP=self.IDENT[:]
                self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            else:
                break
        P("<4")
        return TYP

    def rule_expr4_1(self):#4_1� ������� ��������� - ������� ���������� ��������( - +)
                           #                               
        P(">rule_expr4_1")        
        if self.LEX[self.i][0] in{'-','+'}:
            self.rule_ident() # - +
            self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            TYP=self.rule_expr4_1()
        else:
            TYP=self.rule_expr4_2()
        P("<4_1")
        return TYP

    def rule_expr4_2(self):#4_2� ������� ��������� - [] () .     #����������� � ����� ���������� ����� �������
        NL=len(self.GEN.expr) #�������� ������� ������ � ������ ������ ���������
        TYP=self.rule_expr7() 
        while self.LEX[self.i][0] in{'[','(','.'}:
            if self.LEX[self.i][0] in{'['}:
                TYP=self.rule_expr5(TYP)
            elif self.LEX[self.i][0] in{'('}:
                #���� ����� ������ �����, �� ��� �����, ����� �-��� �� �������
                dcl_l  =  self.decls  if self.LEX[self.i-2][0]!='.'  else  self.inner_decls
                decls=self.find_id_decl_list(self.LEX[self.i-1][0],dcl_l)  #������� ��� decl-� ��� ����� �����
                TYP=self.rule_expr5_1(TYP,decls)
            else:    #self.LEX[self.i][0] in{'.'}
                TYP=self.rule_expr6(TYP)
        return TYP 


    def get_array_startIndexes(self,td):
        L=[]    
        i=0
        while td[i]=='array':
            i+=2 #'array' '['
            while True:
                minv=int(td[i])
                i+=2 #minv '..'
                maxv=int(td[i])
                i+=1
                L.append(minv) 
                if td[i]!=',':
                    break
                i+=1 #','            
            i+=2 #']' 'of'
        return (L,td[i:])

    def rule_expr5(self,TYP):#5� ������� ��������� - �������� ��������� � �������� �������( [] )
        P(">rule_expr5")        
        if self.LEX[self.i][0] in{'['} and TYP[3][0]=='array':
            dt=self.get_array_startIndexes(TYP[3])
            i=0
            while self.LEX[self.i][0] in{'['} and not(  (self.LEX[self.i][0] in VYRKONSET) and (self.LEX[self.i][1] in {'swrd','sign'})  ):
                self.rule_sym('[')
                self.GEN.expr2('[','sign')
                self.rule_expr1()
                self.GEN.expr+='-'+str(dt[0][i])   #�������� n-� ������ ������� � ����
                i+=1
                while self.LEX[self.i][0] in{','}:
                    self.rule_sym(',')
                    self.GEN.expr2(']','sign')
                    self.GEN.expr2('[','sign')
                    self.rule_expr1()
                    self.GEN.expr+='-'+str(dt[0][i])    #�������� n-� ������ ������� � ����
                    i+=1
                self.rule_sym(']')
                self.GEN.expr2(']','sign')
            P("<5 "+str(dt[1]))
            return self.create_record_decl_list(self.resolve_type(['v','',1,dt[1],[]]))    #���������� ��� �������� �������
        elif  self.LEX[self.i][0] in{'['} and TYP[3][0]=='���':
            self.rule_sym('[')
            self.GEN.expr2('[','sign')
            self.rule_expr1()
            self.GEN.expr+='-1'   #�������� n-� ������ ������ � ����
            self.rule_sym(']')
            self.GEN.expr2(']','sign')
            P("<5")
            return ['v','',1,['���'],[]] 
        else:
            P("<5")
            return TYP

    def issubclass(self,T1,T2):  #�������� �� T2 ���������� T1, ��� T1 � T2 - ������� ������ �����
        #��������, �������� �� ������� ������������� ���� 1

        print ">>>>>",T2

        def get_parents_list(cl_n):#�������� ������ ������� �� ����� ������
            L=[]
            try:
                dcl=self.find_id_decl(cl_n)
                L.extend(dcl[5][0])
                for i in dcl[5][0]:
                    L.extend(get_parents_list(i))
            except:
                pass 
            return L

        print ">>>issubclass0"
        is_var_decl1=False
        dcl1=None
        try:
            dcl1=self.find_id_decl(T1[0])
            is_var_decl1=True
            print ">>>issubclass1"
        except:
            pass 
        #��������, �������� �� ������� ������������� ���� 2
        is_var_decl2=False
        dcl2=None
        try:
            dcl2=self.find_id_decl(T2[0])
            is_var_decl2=True
            print ">>>issubclass2"
        except:
            pass 
        #
        try:
            L=get_parents_list(dcl2[1])
            print ">>>issubclass3",L
            return is_var_decl1 and is_var_decl2 and (dcl1[1] in L)
        except:
            print ">>>issubclass3.1"
            return False

    def rule_expr5_1(self,TYP,dcl_l=[]):#5_1� ������� ��������� - �������� ������ �-��� ( () )
                            # dcl_l -- ������ decl-�� �-��� � ��������� ������
        def types_compatible(T1,isVal,T2): #���� ���������� (T1 � T2 - ������� ������ �����,isVal - �������� ���������� �� ��������)
            if T2[0]=='���':
                T2=[T2[1]]
            #���� �� ��������:
            #��� ����������� ��������� T1 ��������� � ����� ������������ T2, ���� ��� ���������, ���� ���������� ������� � ������, ���� ���������� ������ � �������
            #���� �� ������:
            #��� ����������� ��������� T1 ��������� � ����� ������������ T2, ���� ���� ���������
            #���� ����������� ����� � ��������
            return isVal and (\
			T1==T2 or ((T1[0]=='���' and T2[0]=='���')or(T1[0]=='���' and T2[0]=='���')) and not(len(T1)>1 and len(T2)>1 and (T1[1]=='���' or T2[1]=='���'))  \
                   )or \
                        T1==T2 \
                    or \
                        self.issubclass(T1,T2)
        self.rule_sym('(')
        self.GEN.expr2('(','sign')
        P(">rule_expr5_1") 
        N0=len(self.GEN.expr) 
        TS=[]  #���� ����������� ��������, ������������ �-� ��������� �-���
        l_marg=[]
        r_marg=[]
        while self.LEX[self.i][0]!=')':
            l_marg.append(len(self.GEN.expr))
            T1=self.rule_expr1()  
            r_marg.append(len(self.GEN.expr))
            TS.append(T1[:])
            if self.LEX[self.i][0]==',':
                self.rule_sym(',')
        #��������� ������ �-��� � ����� �� ����������� ���������� => dcl_l1
        # 
        print ">>self.inner_decls",self.inner_decls
        print ">>dcl_l",dcl_l
        if '--no-debug' not in sys.argv:
            raw_input()
        dcl_l1=[]
        for i in dcl_l:
            if len(i[4])==len(TS):
                dcl_l1.append(i[:])
        print ">>dcl_l1",dcl_l1
        if '--no-debug' not in sys.argv:
            raw_input()
        #��������� ������ �-��� � ������������ ������ ���������� => dcl_l2
        # 
        dcl_l2=[] 
        for i in dcl_l1:
            b=True
            for j in range(len(TS)):
                b=b and types_compatible(i[4][j][0],i[4][j][1],TS[j][3][:])
            if b:
                dcl_l2.append(i)
        print ">>dcl_l2",dcl_l2
        if '--no-debug' not in sys.argv:
            raw_input()
        #�������� �-���(����� ������ ���������� �-��� �� ���������)
        #
        dcl=dcl_l2[0][:]
        #
        expr=""
        for j in range(len(TS)):
            ex_s=self.GEN.expr[l_marg[j]:r_marg[j]] 
            if dcl[4][j][0][0]=='���' and TS[j][3][0]=='���':
                ex_s='string(1,'+ex_s+')'
            expr+=ex_s+','
        self.GEN.expr=self.GEN.expr[:N0]  
        self.GEN.expr+=expr[:-1]  #(������� ��������� ������� �� ���������)
        #
        self.rule_sym(')')
        self.GEN.expr2(')','sign')
        P("<5_1")
        return TYP

    def rule_expr6(self,TYP):#6� ������� ��������� - ��������( .(��������� � ���� �������) )
        P(">rule_expr6")        
        if True:
            while self.LEX[self.i][0] in{'.'} and not(  (self.LEX[self.i][0] in VYRKONSET) and (self.LEX[self.i][1] in {'swrd','sign'})  ):
                TYP=self.resolve_type(TYP)[:]
                TYP=self.create_record_decl_list(TYP)
                TYP[0]='v'  #�������, ��� �������� - ����������(���������)
                self.rule_sym('.')
                self.cat_lex()
                self.GEN.expr2('->','sign')
                self.rule_ident()
                print TYP
                self.inner_decls=[ TYP[-1][1][:] ]
                for i in reversed(TYP[-1][1]): #���� ���� ������� � ������������ �����
                    if i[1]==self.IDENT:
                        TYP=i[:]
                        TYP[0]='v'
                        break
                self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
                if TYP[2] in {'2','3'} and self.LEX[self.i][0]!='(':   # �������������� (��������� ������ � ������ �-���)
                    self.GEN.expr+="()"
        P("<6")
        return TYP

    def rule_expr7_1(self):  #�������� new(���)
        P(">new") 
        self.rule_sym('���')
        self.GEN.expr2('new','swrd')
        self.GEN.expr2(' ','iden')
        self.GEN.expr2(self.LEX[self.i][0],'iden')       

        #
        TYP0=self.find_id_decl(self.LEX[self.i][0])
        found=False
        decls=[]
        for i in reversed(TYP0[-1][1]): #���� ���� ������� � ������������ �����
            if i[1]=='�����������':
                found=True
                TYP=i[:]
                TYP[0]='v'
                decls.append(TYP)
        print "found=",found
        if not found:
            TYP=['v','�����������','0','',[],[]] 
        #TYP <= dcl ������������ 
        
        self.rule_ident()
        if self.LEX[self.i][0]=='(':
            self.rule_expr5_1(TYP,decls) #������� ������ �-���

        return TYP0

    def rule_expr7(self):#7� ������� ��������� - ��������� ��������(������������� ���� ��������� ���� ������)
        self.cat_lex()
        P(">rule_expr7")   
        if self.LEX[self.i][0]=='���':
            return self.rule_expr7_1()             
        elif self.LEX[self.i][0]=='������':  
            self.rule_sym('sizeof')
            self.GEN.expr2('sizeof','sign')
            self.rule_sym('(')
            self.GEN.expr2('(','sign')
            self.rule_expr1()
            self.rule_sym(')')
            self.GEN.expr2(')','sign')
            return ['c','','1',['���'],[]] 
        elif self.LEX[self.i][1]=='iden':
            self.rule_ident()
            IDENT=self.IDENT[:]
            if True:
                dcl=['t',IDENT,'0',[IDENT],[],None] if IDENT in BASICTYPES else self.find_id_decl(self.IDENT)
                if dcl[0]=='t': #������ ������-������������� ��� ��� (�����-����������)          
                    #dcl=self.resolve_type(dcl)
                    self.rule_sym('(')                #��� ������� ���� 
                    N1=len(self.GEN.expr)
                    T1=self.resolve_type(self.rule_expr1())
                    T2=dcl
                    self.rule_sym(')')
                    if T1[3][0]=='���' and T2[3][0]=='���':  #�������������� ����������� char->string
                        self.GEN.expr=self.GEN.expr[:N1]+'string(1,'+self.GEN.expr[N1:]+')'
                    else:
                        self.GEN.expr=self.GEN.expr[:N1]+'(('+typeconv(IDENT)+')('+self.GEN.expr[N1:]+'))'
                    return dcl[:]
            #print dcl
            dcl=self.create_record_decl_list(self.resolve_type(dcl))
            if self.LEX[self.i-1][0] == '����' and self.LEX[self.i][0]==':=':        # �������:������������ ����.�����-� ������ ����-� �-���
                self.GEN.expr2('_result','iden')
            elif dcl[2] in {'2','3'} and self.LEX[self.i][0]!='(':   # �������������� (��������� ������ � ������ �-���)
                self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
                self.GEN.expr+="()"
            else:
                self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            return dcl
        elif self.LEX[self.i][1]=='stra':
            self.rule_ident()
            self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            return ['c','',1,['���'],[]]
        elif self.LEX[self.i][1]=='char':
            self.rule_ident()
            self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            return  ['c','',1,['���'],[]]
        elif self.LEX[self.i][1]=='inum':
            self.rule_ident()
            self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            return  ['c','',1,['���'],[]]
        elif self.LEX[self.i][1]=='fnum':
            self.rule_ident()
            self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            return  ['c','',1,['���'],[]]
        elif self.LEX[self.i][1]=='bool':
            self.rule_ident()
            self.GEN.expr2(self.IDENT,self.IDENT_TYPE)
            return  ['c','',1,['���'],[]]
        elif self.LEX[self.i][0]=='(':
            self.rule_sym('(')
            self.GEN.expr2('(','sign')
            TYP=self.rule_expr1()
            self.rule_sym(')')
            self.GEN.expr2(')','sign')
            return TYP
        elif self.LEX[self.i][0]=='���':
            self.rule_sym('���')
            self.GEN.expr2('���','swrd')
            print '********************************B'
            #raw_input()
            dc=self.find_id_decl(self.class_name1)[:]
            print '********************************E'
            #raw_input()
            dc[0]='v'
            return dc
        #elif self.LEX[self.i][0]=='��':  #��� ����������  ��
        #    return self.rule_expr2_1()
        else:
            print 'ERR',self.LEX[self.i]
            raw_input()

    '''def rule_type_file(self,D_LEVEL=0): #������ ���������������� �����
        P(">rule_type_file")
        self.rule_sym('����')  
        self.GEN.incl_pfile()
        self.TYPE_D='pfile_u*'
        return (['����'],)'''
    def rule_type_integer(self,D_LEVEL=0):
        P(">rule_type_integer")
        self.rule_sym('���')  
        self.TYPE_D='int'
        return (['���'],)
    def rule_type_array(self,D_LEVEL=0):
        P(">rule_type_array")
        N0=self.i        
        self.TYPE_D=''    
        self.rule_sym('array') 
        self.rule_sym('[')         
        while True:
            self.rule_ident()  
            minv=int(self.IDENT)
            self.rule_sym('..')
            self.rule_ident()  
            maxv=int(self.IDENT)
            self.TYPE_D+='['+str(maxv-minv+1)+']'
            if self.LEX[self.i][0]!=',':
                break
            self.rule_sym(',')            
        self.rule_sym(']')
        self.rule_sym('of')
        TYPE_D=self.TYPE_D
        N1=self.i
        CHN=self.rule_type_description(D_LEVEL+1)
        #
        jj=len(self.TYPE_D)-1
        while jj>=0 and self.TYPE_D[jj]==']':
            while jj>=0 and self.TYPE_D[jj]!='[':
                jj-=1
            if jj>=0: 
                jj-=1
        #
        self.TYPE_D=self.TYPE_D[:jj+1]+TYPE_D+self.TYPE_D[jj+1:]
        return ([i[0] for i in self.LEX[N0:N1]]+CHN[0],)
    def rule_type_char(self,D_LEVEL=0):
        P(">rule_type_char")
        self.rule_sym('���')  
        self.TYPE_D='char'
        return (['���'],)
    def rule_type_string(self,D_LEVEL=0):
        P(">rule_type_string")
        self.rule_sym('���')  
        self.GEN.incl_string()
        self.TYPE_D='string'
        return (['���'],)
    def rule_type_description(self,D_LEVEL=0,TNAME=""):   #D_LEVEL - ������� ����������� ��������� � �����������,TNAME-��� ���� ��� type ������
        P(">type_description")
        res=None
        if self.LEX[self.i][1]=='���':
            return self.rule_type_array(D_LEVEL+1)
        elif self.LEX[self.i][0]=='���':
            return self.rule_type_string(D_LEVEL+1)
        elif self.LEX[self.i][0]=='���':
            return self.rule_type_integer(D_LEVEL+1)
        elif self.LEX[self.i][0]=='���':
            return self.rule_type_char(D_LEVEL+1)
        elif self.LEX[self.i][0]=='���':
            self.rule_ident()
            self.TYPE_D='float'
            return (['���'],)
        elif self.LEX[self.i][0]=='���':
            self.rule_ident()
            self.TYPE_D='bool'
            return (['���'],)
        #elif self.LEX[self.i][0] in {'����'}:
        #    return self.rule_type_file(D_LEVEL+1)
        else:
            self.rule_ident()
            self.TYPE_D=self.IDENT[:] + '*'
            return ([self.IDENT[:]],) 


    def rule_uses(self):    #������ ���������� ��� ������������ �����  #include "���_������.h" |  �������������� ������ (uses �����.�����.������) -- ������������� � ��������
        global UNITS
        P("USES")
        self.rule_sym('������������')
        IDENTS=[]
        while True:
            PACKETS=[]
            while True:
                self.rule_ident()
                PACKETS.append(perform_cyr(self.IDENT[:]))
                if self.LEX[self.i][0]!='.':
                    break
                self.rule_sym('.')
            oo=open("units/"+"/".join(PACKETS)+".ku","rb")
            o=pickle.load(oo)
            for i in o["UNITS"]:
                if i not in UNITS:
                    UNITS.append(i[:])
            for i in o["unit_init_procs"]:
                if i not in UNITS_INIT_PROCS:
                    UNITS_INIT_PROCS.append(i[:])
            self.decls.extend(o["decls"]) 
            repl.update(o["repl"])  #��������� ������ ��������������� �� ������
            oo.close()
            IDENTS.append("/".join(PACKETS))
            if self.LEX[self.i][0]==';':
                self.rule_sym(';')
                break
            self.rule_sym(',')
        self.GEN.uses(IDENTS)

    def rule_object_data_entry(self,record_num,dt,o_decls,D_LEVEL=0):  #   k,m:char <;>
        P(">rule_object_data_entry")

        N1=self.i #��� ������� �����������
        CHN=self.rule_type_description()   #type

        IDENTS=[]
        while True:
            self.cat_lex()
            self.rule_ident()        
            IDENTS.append(self.IDENT)
            if self.LEX[self.i][0]==';':
                self.rule_sym(';')                
                break
            else: 
                self.rule_sym(',') 

        self.GEN.object_data_entry(IDENTS,self.TYPE_D,dt)
        N2=self.i #��� ������� �����������
        D=o_decls  #��������� � ������ ����������� �������
        for ii in IDENTS:
                dcl=['v',ii,'1',CHN[0],[] ]
                if len(CHN)>1:
                    dcl.append(CHN[1])
                else:
                    dcl.append(None)
                D.append(dcl)
        
        self.semicolons()  
    def has_func_body(self):
        "�-��� ����� ���� ������ ����������� ������. �����������: �� ��������� �� ������ ����� ����� ����������� ��������� � ������"
        j=self.i
        res=[False]
        while True:
            if self.LEX[j][0]=='���' or self.LEX[j][0]=='��' or self.LEX[j][0]=='���_���' or self.LEX[j][0]=='���' and (j<len(self.LEX) and self.LEX[j+1][0]=='���'):
                res=[False]
                break
            elif self.LEX[j][0]=='���' and (j<len(self.LEX) or self.LEX[j+1][0]!='���'):
                res=[True,j+1]
                break
            j+=1 
        return res
            
    def rule_object_func_entry(self,record_num,dt,o_decls,D_LEVEL=0,TNAME=""):
        P(">rule_object_func_entry")

        NB=self.i #*

        self.rule_sym('���')

        #��������, �������� �� ����� 2� �������������
        is_var_decl=False
        dcl=None
        try:
            dcl=self.find_id_decl(self.LEX[self.i][0])
        except:
            pass 
        if (self.LEX[self.i][0] in BASICTYPES or (not dcl is None and dcl[0]=='t')):
            is_var_decl=True
        if is_var_decl:  #��� ���
            N1=self.i #��� ������� �����������
            CHN=self.rule_type_description()    
            N2=self.i #��� ������� �����������
            TYPE_D0=self.TYPE_D[:]
        else:
            CHN=([''],)
            TYPE_D0='void'

        isMethod=False
        class_name=''

        NN=self.i #*            �����, ���� ���� ���� �������� ��� ������ � ����������� ���� �-���  (��� ��������)

        self.cat_lex()
        self.rule_ident()      #��� �-���
        FNAME=self.IDENT[:]
        self.GEN.par_list1()  #������� ����� ������ ����������

        ##self.decls.append([])
        if self.LEX[self.i][0]=='(':  #������ ���������� � �������
            PTL=self.rule_func_par_list(GEN_DEC=False)
        else:
            PTL=[] 
        
        NV=self.i   #*  ����� ����� ������  ���� , ����� ������ ��� �� ������������ ���� �-���

        if self.LEX[self.i][0]=='����':
            virtual=True
            self.rule_sym('����')
        else:
            virtual=False

        self.GEN.o_func_zag(FNAME,TYPE_D0,dt,virtual,TNAME)

        D=o_decls  #��������� � ������ �����������
        dcl=['v',FNAME,'3',CHN[0],PTL ]
        if len(CHN)>1:
            dcl.append(CHN[1])
        else:
            dcl.append(None)
        D.append(dcl)

        self.semicolons()

        NE=self.i #*

        RES=self.has_func_body() #*
        if RES[0]==True:         #*  
            self.LEX, V =self.LEX[:NE]+self.LEX[RES[1]:],   [[';','sign']]+self.LEX[NB:NN]+[[self.TRclass_name,'iden']]+[['.','sign']]+self.LEX[NN:NV]+[[';','sign']]+self.LEX[NE:RES[1]]+[[';','sign']]       #*    self.LEX[NB:RES[1]]  #
            #T=self.LEX[NE-5:NE]+self.LEX[RES[1]:RES[1]+10]
            print ">>>",unicode(" ".join([i[0] for i in V]),'cp1251'),"   ",NB,RES[1]       #*
            #print ">>>",unicode(" ".join([i[0] for i in T]),'cp1251'),"   ",unicode(self.LEX[self.i][0],"cp1251")       #*
            self.semicolons()
            if '--no-debug' not in sys.argv:
                raw_input()        #*   ����: ����� ������������ ���� �-���
            self.TRmethod_buf+=V
            pass                 #*
    def rule_type_object(self,D_LEVEL=0):
        global PREFIX,interface_mode
        self.TRmethod_buf=[]     #* ��� �������� ������� �� ������
        P(">rule_type_object")
        N0=self.i
        o_decls=[]  #���������� � ������
        parents=[]
        dt=[""]  #����� ��� ������������ ����������� ������

        self.rule_sym('���')

        self.rule_ident()
        TNAME=self.IDENT[:]
        self.TRclass_name=TNAME[:]

        if self.LEX[self.i][0]=='(':  #������ (�� ���������)
                self.rule_sym('(') 
                while True:
                    self.rule_ident() 
                    parents.append(self.IDENT)
                    if self.LEX[self.i][0]!=',':
                        break
                    else:
                        self.rule_sym(',')  
                self.rule_sym(')') 

        self.semicolons()

        self.GEN.struct1(self.record_num,dt,parents,TNAME)
        while self.LEX[self.i][0] not in {'��','���','���_���'}:
            if self.LEX[self.i][0]=='���':
                self.rule_object_func_entry(self.record_num,dt,o_decls,D_LEVEL+1,TNAME)
            elif self.LEX[self.i][0]=='����': #public
                self.rule_sym('����')
                self.semicolons()
                dt[0]+='public:\r\n'
            elif self.LEX[self.i][0]=='����': #private
                self.rule_sym('����')
                self.semicolons()
                dt[0]+='private:\r\n'
            elif self.LEX[self.i][0]=='���':  #protected
                self.rule_sym('���')
                self.semicolons()
                dt[0]+='protected:\r\n'
            else:
                self.rule_object_data_entry(self.record_num,dt,o_decls,D_LEVEL+1)
        if self.LEX[self.i][0]=='��':
            self.rule_sym('��')
        elif self.LEX[self.i][0]=='���':
            self.rule_sym('���')
            self.rule_sym('���')
        elif self.LEX[self.i][0]=='���_���':
            self.rule_sym('���_���')
        self.semicolons()
        self.GEN.struct2(dt)
        self.TYPE_D=TNAME
        self.record_num+=1
        #��������� ����������� �� ������� � ����������� �������� �������:
        for i in parents:
            dcl=self.find_id_decl(i)
            o_decls=dcl[5][1]+o_decls
        #
        N1=self.i
        
        #######�������� ��������� ������ ���������� � ������� => ���������� ��� ����
        #######
        CHN=([i[0] for i in self.LEX[N0:N1]],(parents,o_decls))
        D=self.decls[len(self.decls)-1]  #��������� � ������ �����������
        dcl=['t',TNAME,'0',CHN[0],[]]
        dcl.append(CHN[1])        
        D.append(dcl)

        self.LEX = self.LEX[:self.i] + self.TRmethod_buf + self.LEX[self.i:] #*  ������� ���������� ��� ������� �� ������
        interface_mode=False
    def rule_var_section(self):
        P(">rule_var_section")

        N1=self.i #��� ������� �����������
        CHN=self.rule_type_description()   #type

        self.var_list=[]
        while True:
            self.cat_lex()
            self.rule_ident()        
            self.var_list.append(self.IDENT)
            if self.LEX[self.i][0]==';':
                self.semicolons()                
                break
            else: 
                self.rule_sym(',') 


        self.GEN.var(self.var_list,self.TYPE_D)
        N2=self.i #��� ������� �����������
        D=self.decls[len(self.decls)-1]  #��������� � ������ �����������
        for ii in self.var_list:
            dcl=['v',ii,'1',CHN[0],[] ]
            if len(CHN)>1:
                dcl.append(CHN[1])
            else:
                dcl.append(None) 
            D.append(dcl)

    def times_cycle(self):
        N=len(self.GEN.curr_code[0])
        self.rule_expr()
        self.rule_sym('���') 
        self.GEN.curr_code[0],e = self.GEN.curr_code[0][:N], self.GEN.curr_code[0][N:]
        s=str(self.temp_var_n)+perform_cyr(PNAME)
        self.temp_var_n+=1
        self.GEN.ADD( ('for(int _temp_i%s=0;_temp_i%s<'+e+';_temp_i%s++)') % (s,s,s) )
        self.semicolons() 
        self.rule_block()
    def infinite_cycle(self):
        self.GEN.while_true()
        self.semicolons() 
        self.rule_block()
    def rule_while(self):
        P(">rule_while")
        self.GEN.while1()
        self.rule_sym('����')   
        self.rule_expr()
        self.GEN.while2()
        self.semicolons() 
        self.rule_block()
    def rule_for(self):
        P(">rule_for")
        self.rule_sym('���') 
        self.cat_lex()
        FOR_ID=self.LEX[self.i][0]
        self.GEN.for1(FOR_ID)
        self.rule_ident()  
        self.rule_sym('��') 
        self.rule_expr()
        self.GEN.for2(FOR_ID)
        self.rule_sym('��') 
        self.rule_expr()
        self.GEN.for3(FOR_ID)
        self.semicolons()
        self.rule_block()
    def rule_cikl(self):
        P(">rule_cycle")
        self.rule_sym('��') 
        if self.LEX[self.i][0]=='���':
            self.rule_for()
        elif self.LEX[self.i][0]=='����':
            self.rule_while()
        elif self.LEX[self.i][0]==';':
            self.infinite_cycle()
        else:
            self.times_cycle()
        self.rule_sym('��') 
        #
        if self.LEX[self.i][0]=='���':  #����: �� �� ��� (���)
            self.rule_sym('���')
            N=len(self.GEN.curr_code[0])
            self.rule_expr()
            self.GEN.curr_code[0],e = self.GEN.curr_code[0][:N],self.GEN.curr_code[0][N:]
            #������� ������� �� ����� ����� ������������
            while self.GEN.curr_code[0][-1]!='}':
                self.GEN.curr_code[0]=self.GEN.curr_code[0][:-1]
            self.GEN.curr_code[0]=self.GEN.curr_code[0][:-1] 
            #
            self.GEN.curr_code[0]+='    if('+e+') break;\r\n'
            self.GEN.ADD('}')


    def rule_utv(self):
        P(">rule_utv")
        self.GEN.utv1()
        self.rule_sym('���')  
        self.rule_expr()
        self.GEN.utv2()

    def rule_dano(self):  #���������� ��� ����������� ���
        P(">rule_dano")
        self.GEN.utv1()
        self.rule_sym('����')  
        self.rule_expr()
        self.GEN.utv2()
    def rule_nado(self):
        P(">rule_nado")
        N=len(self.GEN.curr_code[0])
        self.GEN.utv1()
        self.rule_sym('����')  
        self.rule_expr()
        self.GEN.utv2()
        self.GEN.nado=self.GEN.curr_code[0][N:]
        self.GEN.curr_code[0]=self.GEN.curr_code[0][:N]

    def rule_if(self):
        P(">rule_if")
        self.GEN.if1()
        self.rule_sym('����')   
        self.rule_expr()
        self.semicolons()
        self.rule_sym('��') 
        self.semicolons()
        self.GEN.if2()
        self.rule_block()
        if self.LEX[self.i][0]=='�����':
            self.GEN.if_else()
            self.rule_sym('�����')
            self.semicolons()
            self.rule_block() 
        self.rule_sym('���')

    def rule_empty_operator(self):
        P("rule_empty_operator")
        #self.GEN.ADD("")   #�������� ������
        if self.LEX[self.i][0]==';':
            self.semicolons() 

    def rule_vybor_pri(self):
        self.GEN.if1()
        self.rule_sym('���')
        self.rule_expr()
        self.rule_sym(':') 
        self.semicolons()
        self.GEN.if2()
        self.rule_block()
        self.GEN.if_else()
        self.semicolons()

    def vybor_inache(self):
        self.rule_sym('�����')        
        self.semicolons()
        self.rule_block()
        self.semicolons()

    def rule_vybor(self):
        self.rule_sym('�����')   
        self.semicolons()
        while self.LEX[self.i][0]!='���':
            if self.LEX[self.i][0]=='���':
                self.rule_vybor_pri()
            else:
                self.vybor_inache()
        self.rule_sym('���')
        self.semicolons()

    def rule_write(self):
        P(">rule_write")
        self.GEN.incl_iostream()
        self.GEN.write1()
        self.rule_sym('�����')   
        while self.LEX[self.i][0]!=';':
            self.GEN.write2()
            if self.LEX[self.i][0]=='��':
                self.GEN.curr_code[0]+='endl'
                self.rule_sym('��')
            else:   
                self.rule_expr()
            if self.LEX[self.i][0]==',':
                self.rule_sym(',') 
        self.GEN.write3()

    def rule_read(self):
        P(">rule_read")
        self.GEN.incl_iostream()
        self.GEN.read1()
        self.rule_sym('����')   
        while self.LEX[self.i][0]!=';':
            self.GEN.read2()
            self.rule_expr()
            if self.LEX[self.i][0]==',':
                self.rule_sym(',') 
        self.GEN.read3()

    def rule_operator(self):  #�������� ������ ���������
        P("rule_operator")
        if self.LEX[self.i][0]=='����':
            self.rule_if()
        elif self.LEX[self.i][0]=='��':
            self.rule_cikl()
        elif self.LEX[self.i][0]=='�����':
            self.rule_write()
        elif self.LEX[self.i][0]=='����':
            self.rule_read()
        elif self.LEX[self.i][0]=='�����':
            self.rule_sym('�����')
            self.GEN.ADD('break')
        elif self.LEX[self.i][0]=='�����':
            self.rule_vybor()
        elif self.LEX[self.i][0]=='�������':
            self.rule_sym('�������')
            self.GEN.ADD('delete ')
            self.rule_expr()
        elif self.LEX[self.i][0]=='���':
            self.rule_utv()
        elif self.LEX[self.i][0] in {';','���','��'}:
            self.rule_empty_operator()
        else: 		#��� ��������� ���� ����������� ����������
            is_var_decl=False
            dcl=None
            try:
                dcl=self.find_id_decl(self.LEX[self.i][0])
                print dcl
                print 'yes'
            except:
                pass 
            if (self.LEX[self.i][0] in BASICTYPES or (not dcl is None and dcl[0]=='t')) and (self.LEX[self.i+1][0]!='('):
                is_var_decl=True
            if is_var_decl:  #��� ����������� ����������
                self.rule_var_section()
            else:            #��� ���������
                self.GEN.ADD("")   #�������� ������
                self.rule_expr()
        self.GEN.end_operator_semicolon()

    def rule_func_block(self):  #���� ���-��� �������
        P("FUNC_BLOCK")
        if self.LEX[self.i][0]=='���':   #��� ��������������, �������, ��� ��� �-��� -- ���
            self.rule_sym('���')
        if self.LEVEL==0:
            self.GEN.OTSTUP=1   #�������� ������
        while self.LEX[self.i][0]!='���':
            self.rule_operator()
            self.semicolons()    
        self.rule_sym('���')
        self.semicolons() 

    def rule_block(self):  #���������� ���� � ����
        P("FUNC_BLOCK")
        self.semicolons()   
        self.GEN.block_begin()
        self.GEN.OTSTUP+=1   #�������� ������
        while self.LEX[self.i][0] not in {'��','���','�����','���'}:
            self.rule_operator()
            self.semicolons()    
        self.GEN.OTSTUP-=1
        self.GEN.block_end()

    def rule_gblock(self):   #���� ���-���-��� ���������� ���������
        self.GEN.nado_b()
        P("BLOCK")
        self.rule_sym('���')
        self.semicolons()
        if self.LEX[self.i][0]=='����':   #��������������
            self.rule_dano()
            self.semicolons()  
        if self.LEX[self.i][0]=='����':   #��������������
            self.rule_nado()
            self.semicolons()  
        if self.LEX[self.i][0]=='���':
            self.rule_sym('���')     #��� ��������������, �������, ��� ��� �-��� -- ���
        N=len(self.decls)        #��������� ������ ����������� ��� ���������� �����
        self.decls.append([])    #
        self.GEN.gblock_begin()
        self.GEN.OTSTUP=1   #���������� ������
        while self.LEX[self.i][0]!='���':
            self.rule_operator()
            self.semicolons()    
        self.rule_sym('���')
        self.semicolons() 
        self.GEN.nado_e()
        self.GEN.gblock_end()
        self.decls=self.decls[:N]      #���������� � �������� ��������� ������ �����������

    def semicolons(self):
        while self.i<len(self.LEX) and self.LEX[self.i][0]==';':
            self.rule_sym(';')

    def rule_func_par_list_entry(self,GEN_DEC=True):  #   ���|������|���|(�����) ��� k,m <,>
        P(">rule_func_par_list_entry")

        if self.LEX[self.i][0]=='���':
            self.rule_sym('���')
            self.last_acs_modifier='���'
        elif self.LEX[self.i][0]=='������':
            self.rule_sym('������')
            self.last_acs_modifier='������'
        elif self.LEX[self.i][0]=='���':
            self.rule_sym('���')
            self.last_acs_modifier='���'

        self.var_list=[]
        PARTYPELIST=[]

        N1=self.i #��� ������� �����������   
        CHN=self.rule_type_description()   #type

        while True:
            self.cat_lex()
            self.rule_ident()  
            PARTYPELIST.append( [CHN[0][:],self.last_acs_modifier=='���'] ) #��� ������ ����������  
            self.var_list.append(self.IDENT)      
            if self.LEX[self.i][0]==')' or self.LEX[self.i+1][0] in ({'������','���','���'}|BASICTYPES):
                break
            else: 
                self.rule_sym(',')        

        if self.last_acs_modifier=='���':
            self.GEN.par_list_entry(self.var_list,self.TYPE_D)
        else: #��� ������
            self.GEN.par_list_var_entry(self.var_list,self.TYPE_D)
        
        N2=self.i #��� ������� �����������
        if GEN_DEC:
            D=self.decls[len(self.decls)-1]  #��������� � ������ �����������
            for ii in self.var_list:
                dcl=['v',ii,'1',CHN[0],[] ]
                if len(CHN)>1:
                    dcl.append(CHN[1])
                D.append(dcl)
        if self.LEX[self.i][0]==';':
            self.rule_sym(';') 
        return PARTYPELIST  

    def rule_func_par_list(self,GEN_DEC=True):     #  (...)
        P("FUNC_PAR_LIST")
        self.last_acs_modifier='���'   #�� ��������� ������ ���������� � ��������� - �� ��������
        self.rule_sym('(')
        PARTYPELIST=[]
        while self.LEX[self.i][0]!=')':
            if self.LEX[self.i][0]==')': #�����
                break
            else:			   #������ ����������
                PARTYPELIST.extend(self.rule_func_par_list_entry(GEN_DEC))
                if self.LEX[self.i][0]==',':
                    self.rule_sym(',')
        self.rule_sym(')')
        return PARTYPELIST

    def rule_function_header(self):   #��� �������� �������(����������� ����� �������� ��� ������ ���������� �-���
        P("FUNCTION")
        N=len(self.decls)  #���������� ������� ����� ������� �����������(����� ������� � �������� ���������)
        self.LEVEL+=1
        self.rule_sym('���')

        #��������, �������� �� ����� 2� �������������
        is_var_decl=False
        dcl=None
        try:
            dcl=self.find_id_decl(self.LEX[self.i][0])
        except:
            pass 
        if (self.LEX[self.i][0] in BASICTYPES or (not dcl is None and dcl[0]=='t' and self.LEX[self.i+1][0]!='.')):
            is_var_decl=True
        if is_var_decl:  #��� ���
            N1=self.i #��� ������� �����������
            CHN=self.rule_type_description()    
            N2=self.i #��� ������� �����������
            TYPE_D0=self.TYPE_D[:]
        else:
            CHN=([''],)
            TYPE_D0='void'

        if self.LEX[self.i+1][0]=='.':  #��� �����
            isMethod=True
            self.rule_ident()  #��� ������
            class_name=self.IDENT[:]
            self.rule_sym('.')
        else:
            isMethod=False
            class_name=''
        self.cat_lex()
        self.rule_ident()      #��� �-���
        FNAME=self.IDENT[:]
        self.GEN.par_list1()  #������� ����� ������ ����������
        if isMethod:
            dcl=self.find_id_decl(class_name)[5][1]
            self.decls.append(dcl)
        self.decls.append([])
        if self.LEX[self.i][0]=='(':  #������ ���������� � �������
            PTL=self.rule_func_par_list()
        else:
            PTL=[] 
        
        if CHN[0][0]=='':
            self.GEN.proc1header(FNAME,self.LEVEL,class_name)            
        else:
            self.GEN.func1header(FNAME,TYPE_D0,self.LEVEL,class_name)
        if not isMethod:  #���� �����, �� ��������� � ���������� ������ �� ����, ��� ������ ���.����������� � ������ ������(� ���������)
            D=self.decls[len(self.decls)-2]  #��������� � ������ �����������
            dcl=['v',FNAME,'3',CHN[0],PTL ]
            if len(CHN)>1:
                dcl.append(CHN[1])
            else:
                dcl.append(None)
            D.append(dcl)

        ###self.decls[-1].append(['v','����','1',CHN[0],None ]) #��������� ���������� '����' ��� �������� �-��� (� ����� ������ - � ��� ������ � ��� ������� �-���)

        self.semicolons()

        self.LEVEL-=1
        if '--no-debug' in sys.argv:
            pass
        else:
            print FNAME,self.decls
            raw_input()
        self.decls=self.decls[:N]      #���������� � �������� ��������� ������ �����������


    def rule_function(self):
        self.GEN.nado_b()
        P("FUNCTION")
        N=len(self.decls)  #���������� ������� ����� ������� �����������(����� ������� � �������� ���������)
        self.LEVEL+=1
        self.rule_sym('���')

        #��������, �������� �� ����� 2� �������������
        is_var_decl=False
        dcl=None
        try:
            dcl=self.find_id_decl(self.LEX[self.i][0])
        except:
            pass 
        if (self.LEX[self.i][0] in BASICTYPES or (not dcl is None and dcl[0]=='t'  and self.LEX[self.i+1][0]!='.')):
            is_var_decl=True
        if is_var_decl:  #��� ���
            N1=self.i #��� ������� �����������
            CHN=self.rule_type_description()    
            N2=self.i #��� ������� �����������
            TYPE_D0=self.TYPE_D[:]
        else:
            CHN=([''],)
            TYPE_D0='void'

        if self.LEX[self.i+1][0]=='.':  #��� �����
            isMethod=True
            self.rule_ident()  #��� ������
            self.class_name1=self.IDENT[:]
            self.rule_sym('.')
        else:
            isMethod=False
            self.class_name1=''
        self.cat_lex()
        self.rule_ident()      #��� �-���
        FNAME=self.IDENT[:]
        self.GEN.par_list1()  #������� ����� ������ ����������
        if isMethod:
            dcl=self.find_id_decl(self.class_name1)[5][1]
            self.decls.append(dcl)
        self.decls.append([])
        if self.LEX[self.i][0]=='(':  #������ ���������� � �������
            PTL=self.rule_func_par_list()
        else:
            PTL=[] 
        
        if CHN[0][0]=='':
            self.GEN.proc1(FNAME,self.LEVEL,self.class_name1)            
        else:
            self.GEN.func1(FNAME,TYPE_D0,self.LEVEL,self.class_name1)
        if not isMethod:  #���� �����, �� ��������� � ���������� ������ �� ����, ��� ������ ���.����������� � ������ ������(� ���������)
            D=self.decls[len(self.decls)-2]  #��������� � ������ �����������
            dcl=['v',FNAME,'3',CHN[0],PTL ]
            if len(CHN)>1:
                dcl.append(CHN[1])
            else:
                dcl.append(None)
            D.append(dcl)

        self.decls[-1].append(['v','����','1',CHN[0],None ]) #��������� ���������� '����' ��� �������� �-��� (� ����� ������ - � ��� ������ � ��� ������� �-���)

        self.semicolons()
        if self.LEX[self.i][0]=='����':   #��������������
            self.rule_dano()
            self.semicolons()  
        if self.LEX[self.i][0]=='����':   #��������������
            self.rule_nado()
            self.semicolons()  
        if self.LEX[self.i][0]=='���':   #��� ��������������
            self.rule_sym('���')
        #self.GEN.block_begin()
        self.GEN.OTSTUP=1   #�������� ������
        while self.LEX[self.i][0]!='���':
            self.rule_operator()
            self.semicolons()  
        self.rule_sym('���')
        self.GEN.nado_e()
        self.semicolons()
        self.GEN.OTSTUP=0   #�������� ������
        #self.GEN.block_end()
        
        if CHN[0][0]=='':
            self.GEN.proc2()
        else:
            self.GEN.func2()
        self.GEN.dump()
        self.LEVEL-=1
        if '--no-debug' in sys.argv:
            pass
        else:
            print FNAME,self.decls
            raw_input()
        self.decls=self.decls[:N]      #���������� � �������� ��������� ������ �����������


    def rule_prog_operator(self):
        global interface_mode
        if self.LEX[self.i][0]=='���':
            if self.LEX[self.i+1][0] in {';','('}:
                self.rule_gblock()
            else:
                self.rule_function() 
        elif self.LEX[self.i][0]==';':
            self.semicolons()
        elif self.LEX[self.i][0]=='���':  #������ ����������, �.�. ��� �������������� �� ������� �������
            while self.i<len(self.LEX) and not(self.LEX[self.i][0] in {'��','���_���'} and self.LEX[self.i][1]=='swrd'  or  self.LEX[self.i][0]=='���' and self.LEX[self.i+1][0]=='���' and self.LEX[self.i][1]=='swrd'):
                self.i+=1
            if self.LEX[self.i][0] in {'��','���_���'}:#��������� � �� �� ��������� �����
                self.i+=1   
            else: #��� ���
                self.i+=2 
        elif self.LEX[self.i][0]=='������������':
            self.rule_uses()
        elif self.LEX[self.i][0]=='���������':
            self.rule_sym('���������')  
            interface_mode=True
            self.semicolons()
        else: 		#��� ��������� ���� ����������� ����������
            is_var_decl=False
            dcl=None
            try:
                dcl=self.find_id_decl(self.LEX[self.i][0])
            except:
                pass 
            if (self.LEX[self.i][0] in BASICTYPES or (not dcl is None and dcl[0]=='t')) and (self.LEX[self.i+1][0]!='('):
                is_var_decl=True
            if is_var_decl:  #��� ����������� ����������
                self.rule_var_section()
            else:            #��� ���������
                self.GEN.ADD("")   #�������� ������
                self.rule_expr()
        self.GEN.end_operator_semicolon()

    def sintanal(self):
        self.GEN.init_file()   
        #   
        self.semicolons()
        while self.i<len(self.LEX):
            self.rule_prog_operator()
            self.semicolons()
        #
        self.GEN.dumpg()
        #
        #��� �������:
        if self.GEN.typ==1:
            oo=open(perform_cyr(PNAME)+'.ku','wb')
            pickle.dump({"UNITS":UNITS,"decls":self.decls,"unit_init_procs":UNITS_INIT_PROCS,"repl":repl},oo)
            oo.close()

    def prohod0(self):
        global interface_mode
        while self.i<len(self.LEX) and self.LEX[self.i][0]!='���': #���� ��������� ��������� ���������
            while self.i<len(self.LEX) and self.LEX[self.i][0] not in {'���','���','���������'}:
                self.i+=1
            if self.i>=len(self.LEX):
                break
            if self.LEX[self.i][0]=='���������':
                self.rule_sym('���������')  
                interface_mode=True
                self.semicolons()
            if self.LEX[self.i][0]=='���':
                self.rule_type_object()
        while True:
            if self.LEX[self.i+1][0]!=';':
                self.rule_function_header()
            else:
                self.i+=1  
            while self.i<len(self.LEX) and self.LEX[self.i][0]!='���': #���� ��������� ��������� ���������
                while self.i<len(self.LEX) and self.LEX[self.i][0] not in {'���','���','���������'}:
                    self.i+=1
                if self.i>=len(self.LEX):
                    break
                if self.LEX[self.i][0]=='���������':
                    self.rule_sym('���������')  
                    interface_mode=True
                    self.semicolons()
                if self.LEX[self.i][0]=='���':
                    self.rule_type_object()           
            if self.i>=len(self.LEX):
                break
        self.i=0
           
#====================================== ���� ������������ ������� ===========================================
def catst(s):
    "������� ������� 10,13 �� ����� ������"
    while len(s)>0 and s[-1]in {chr(10),chr(13)}:
        s=s[:-1]
    return s

def process_lexem(s,clas):
    global LEXEMS
    LEXEMS.append([s,clas])
    print u"    LEXEM: "+clas+u"-- "+unicode(s,'cp1251')+u" --"

def minuses_to_numbers():
    global LEXEMS
    i=0
    while i<len(LEXEMS):
        if LEXEMS[i][0]=='-' and LEXEMS[i+1][1] in {'inum','fnum'}:
            LEXEMS[i+1][0]='-'+LEXEMS[i+1][0]
            LEXEMS[i:i+1]=[]
        i+=1

SPECWORDS={'����','�����','��','����','��','��','��','���','���','���','���','���','���','���','���','���_���','����','��','�����','���','�����','���','���','�','���','����','��','��','���','���','���','���','���','���','������','��','��','����','�����','������������','���','�������','���','���','����','����'}  #,'����','����','���'
LEXEMS=[]

def load_replaces():   #��� ����� ��������������� -- ������� ��������� ������ �� ����� � ����������� .replaces
    try:
        f=open(sys.argv[1].split('.')[0]+'.replaces','rb')
        for i in f:
            l=i.strip().split(':')
            repl[l[0]]=l[1]
        f.close()
    except:
        pass
    finally:
        try:
            f.close()
        except:
            pass
load_replaces()
def ident_repl(id):
    if id in repl.keys():
        return repl[id]
    else:
        return id    

try:
    i=open(sys.argv[1],"rb")

    CURR_IDEN_LEVEL=0

    for j in [unicode(i.read(),'utf-8').encode('cp1251')]:   #���� �� ������� �����
        s=catst(j)
        print "STR:'"+s+"'"

        #��������� ������ �� �����
        lex=""
        ci=0

        level=0

        while ci<len(s):  #���� �� �������� �����

            #������� �������� � ����� �-�� ���������
            while s[ci]in{' ',chr(9),'\n','\r'}:
                if s[ci]=='\n':
                    process_lexem(';','swrd')
                ci+=1

            while s[ci]=='|' :
                #��� �������� ����������
                bf=""
                while s[ci]!='\n':
                    bf+=s[ci]
                    ci+=1
                ci+=1
                #��� ��������� ����������� ��������� h-�����
                if len(bf)>1 and bf[1]=='@':
                    GEN.body_prefix += '#include "' +bf[2:-1]+ '"\r\n'
                #
                while s[ci]in{' ',chr(9),'\n','\r'}:
                    ci+=1

            lex+=s[ci]

            if s[ci]>='a' and s[ci]<='z' or s[ci]>='A' and s[ci]<='Z' or (s[ci]>='�' and s[ci]<='�') or (s[ci]>='�' and s[ci]<='�'):
                #��� �������������
                ci+=1
                while ci<len(s) and((s[ci]>='a' and s[ci]<='z')or (s[ci]>='A' and s[ci]<='Z')or (s[ci]>='�' and s[ci]<='�')or (s[ci]>='�' and s[ci]<='�') or s[ci]>='0' and s[ci]<='9' or s[ci]=='_'): 
                    lex+=s[ci]
                    ci+=1
                    #print lex 
                lex=lex.lower()
                if lex in SPECWORDS:
                    if lex in {'��','���'}:
                        process_lexem(lex,'bool')
                    else:
                        process_lexem(lex,'swrd')
                else:
                    process_lexem(lex,'iden')
                lex=""
            elif s[ci] in {'+', '[', ']', ',', ':', '(', ')', '{', '}', '-','.','%','^','>','<','&','|',';','*','//'}:
                if ci<len(s)-1:
                    c2=s[ci]+s[ci+1]
                else:
                    c2=""
                if ci+1<len(s) and c2 in {">=","<>","<=","^.","(.",".)","..","+=","-=","*=","/=","|=","&=","^=",":="}:
                    lex=c2
                    process_lexem(lex,'sign')
                    lex=""
                    ci+=2
                else: #��� �������, ��������� �� 1 �������
                    process_lexem(lex,'sign')
                    lex=""
                    ci+=1
            elif s[ci] in {'='}:
                #������� =, ==
                if s[ci+1]=="=":
                    lex="=="
                    process_lexem(lex,'sign')
                    lex=""
                    ci+=2
                else:
                    process_lexem(lex,'sign')
                    lex=""
                    ci+=1
            elif s[ci]>='0' and s[ci]<='9':
                #��� �����, ������������ � �����
                ci+=1
                while ci<len(s) and(s[ci]>='0' and s[ci]<='9' or (s[ci]=='.' and s[ci+1]!='.')): 
                    lex+=s[ci]
                    ci+=1
                    pass  
                if lex.find('.')==-1:
                    process_lexem(lex,'inum')
                else:
                    process_lexem(lex,'fnum')
                lex=""
            elif s[ci]=="'":
                #��� ������, ����������� � ���������
                ci+=1
                lex=""
                while ci<len(s) and s[ci]<>"'":
                    lex+=s[ci]
                    ci+=1 
                if len(lex)!=1:
                    process_lexem(lex,'stra')
                else:
                    process_lexem(lex,'char')
                lex=""
                ci+=1
            elif s[ci]=='"':
                #��� ������, ����������� � �������
                ci+=1
                lex=""
                while ci<len(s) and s[ci]<>'"':
                    lex+=s[ci]
                    ci+=1 
                if len(lex)!=1:
                    process_lexem(lex,'stra')
                else:
                    process_lexem(lex,'char')
                lex=""
                ci+=1

        #process_lexem("",'eoln')

    minuses_to_numbers()
    print LEXEMS
    if '--no-debug' in sys.argv:
        pass
    else:
        raw_input()
    sa=sint_anal(LEXEMS,GEN)    
    sa.prohod0() 
    sa.sintanal()            
    #print sa.decls 

finally:
    try:
        i.close()
    except:
        pass

print
print 'SUCCESS!'