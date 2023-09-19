@c:\python27\python conv.py k1.kum 
@echo [press to compile]
@pause
@"c:\Program Files\Dev-Cpp\MinGW64\bin\g++.exe" -c k1.cpp -o k1.o -I"C:/Program Files/Dev-Cpp/MinGW64/include" -I"C:/Program Files/Dev-Cpp/MinGW64/x86_64-w64-mingw32/include" -I"C:/Program Files/Dev-Cpp/MinGW64/lib/gcc/x86_64-w64-mingw32/4.9.2/include" -I"C:/Program Files/Dev-Cpp/MinGW64/lib/gcc/x86_64-w64-mingw32/4.9.2/include/c++" -m32
@echo [press to link]
@pause
@"c:\Program Files\Dev-Cpp\MinGW64\bin\g++.exe" k1.o -o k1.exe -L"C:/Program Files/Dev-Cpp/MinGW64/x86_64-w64-mingw32/lib32" -static-libgcc -m32
@echo [press to run]
@pause
@k1.exe
@pause
