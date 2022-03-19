g++ src/server_pthread.cc -o server_computer/serverapp -lpthread

g++ src/server.cc -o server_computer/server 


g++ src/client.cc -o client_computer/c1/clientapp
g++ src/client.cc -o client_computer/c2/clientapp
g++ src/client.cc -o client_computer/c3/clientapp
g++ src/client.cc -o client_computer/c4/clientapp
g++ src/client.cc -o client_computer/c5/clientapp


#注意！运行server和client时一定要进入server_computer 和client_computer目录下面运行！！否则fopen不能工作！
