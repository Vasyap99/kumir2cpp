#include <cstdlib>
#include <string>
#define null 0
using namespace std;


template <typename T>                         //typed files
class pfile_t{
	FILE *f;
	string name;
	bool opened;
public:
	pfile_t(){
		f=null;
		opened=false;
		name="";
	}
	~pfile_t(){
		if(opened)close();
	}	
	void assign(string s){
		name=s;
	}
	void reset(){
		f=fopen(name.c_str(),"rb");
		opened=true;
	}
	void rewrite(){
		f=fopen(name.c_str(),"wb");
		opened=true;
	}
	void append(){
		f=fopen(name.c_str(),"ab");
		opened=true;
	}	
	void close(){
		fclose(f);
		opened=false;
	}
	void seek(unsigned int i){
		fseek(f,i*sizeof(T),0);
	}
	unsigned int filesize(){
		return 0;
	}
	bool eof(){
		return feof(f);
	}
	unsigned int filepos(){
		return ftell(f)/sizeof(T);
	}
	void read(T&d){
		fread(&d,sizeof(T),1,f);
	}
	/*void write(T&d){
		fwrite(&d,sizeof(T),1,f);
	}*/	
	void write(T d){
		fwrite(&d,sizeof(T),1,f);
	}	
};

class pfile_u{                         //untyped files
	FILE *f;
	string name;
	bool opened;
public:
	pfile_u(){
		f=null;
		opened=false;
		name="";
	}
	~pfile_u(){
		if(opened)close();
	}	
	void assign(string s){
		name=s;
	}
	void reset(){
		f=fopen(name.c_str(),"rb");
		opened=true;
	}
	void rewrite(){
		f=fopen(name.c_str(),"wb");
		opened=true;
	}
	void append(){
		f=fopen(name.c_str(),"ab");
		opened=true;
	}	
	void close(){
		fclose(f);
		opened=false;
	}
	void seek(unsigned int i){
		fseek(f,i,0);
	}
	unsigned int filesize(){
		return 0;
	}
	bool eof(){
		return feof(f);
	}
	unsigned int filepos(){
		return ftell(f);
	}
	void blockread(void *d,unsigned int n,unsigned int& result){
		fread(d,512*n,1,f);
                result=0;
	}
	void blockwrite(void *d,unsigned int n,unsigned int& result){
		fwrite(d,512*n,1,f);
                result=0;
	}	
	void blockread(void *d,unsigned int n){
		fread(d,512*n,1,f);
	}
	void blockwrite(void *d,unsigned int n){
		fwrite(d,512*n,1,f);
	}	
};
