/*client.c*/
#include<netinet/in.h>                         // for sockaddr_in  
#include<sys/types.h>                          // for socket  
#include<sys/socket.h>                         // for socket  
#include<stdio.h>                              // for printf  
#include<stdlib.h>                             // for exit  
#include<string.h>                             // for bzero  
#include <unistd.h>
#include<iostream>


#include <arpa/inet.h>

using namespace std;

#define HELLO_WORLD_SERVER_PORT       6666  
#define BUFFER_SIZE                   61440  
#define FILE_NAME_MAX_SIZE            512  
#define SERVER_ADDR                "10.0.0.1"
#define FILE_NAME                  "file.txt"


class Timer
{
    clock_t startT;
    std::string label;//计时内容：有多个计时的时候用于区分
    bool isEnd;//是否已经手动结束计时
public:
    Timer(std::string name = "Time")//创建时开始计时
    {
        startT = clock(); 
        label = name;
        isEnd = false;
    }
    ~Timer()//自动结束计时//对象被销毁时自动结束计时
    {
        if (!isEnd)
        {
            clock_t endT = clock();
            double endtime = (double)(endT - startT) / CLOCKS_PER_SEC;
            std::cout<<label<<": "<< endtime << std::endl;		//s为单位
        }
    }
    void End()//手动结束//手动控制在任意位置处结束计时
    {
        clock_t endT = clock();
        double endtime = (double)(endT - startT) / CLOCKS_PER_SEC;
        std::cout << label << ": " << endtime << "\n"<<std::endl;		//s为单位
        isEnd = true;
    }
};



int main(int argc, char **argv)  
//用法： ./server 参数1 参数2
/*
argc和argv参数在用命令行编译程序时有用。main( int argc, char* argv[], char **env ) 中 
第一个参数，int型的argc，为整型，用来统计程序运行时发送给main函数的命令行参数的个数，在VS中默认值为1。 
第二个参数，char*型的argv[]，为字符串数组，用来存放指向的字符串参数的指针数组，每一个元素指向一个参数。各成员含义如下： 
argv[0]指向程序运行的全路径名 
SERVER_ADDR指向在DOS命令行中执行程序名后的第一个字符串 
argv[2]指向执行程序名后的第二个字符串 
argv[3]指向执行程序名后的第三个字符串 
argv[argc]为NULL 
*/

{  
    // if (argc != 2)  
    // {  
    //     printf("Usage: ./%s ServerIPAddress\n", argv[0]);  
    //     exit(1);  
    // }  

    // 设置一个socket地址结构client_addr, 代表客户机的internet地址和端口  
    struct sockaddr_in client_addr;  
    bzero(&client_addr, sizeof(client_addr));  
    client_addr.sin_family = AF_INET; // internet协议族  
    client_addr.sin_addr.s_addr = htons(INADDR_ANY); // INADDR_ANY表示自动获取本机地址  
    client_addr.sin_port = htons(0); 
    // 如果端口号置为0，则WINDOWS套接口实现将给应用程序分配一个值在1024到5000之间的唯一的端口。

    //htons用来将主机字节顺序转为网络字节顺序
    //网络字节顺序是TCP/IP中规定好的一种数据表示格式，它与具体的CPU类型、操作系统等无关，
    //从而可以保证数据在不同主机之间传输时能够被正确解释，网络字节顺序采用big-endian排序方式。

    // 创建用于internet的流协议(TCP)类型socket，用client_socket代表客户端socket  
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);  
    if (client_socket < 0)  
    {  
        printf("Create Socket Failed!\n");  
        exit(1);  
    }  

    // 把客户端的socketFD和客户端的socket地址结构绑定   
    if (bind(client_socket, (struct sockaddr*)&client_addr, sizeof(client_addr)))  
    {  
        printf("Client Bind Port Failed!\n");  
        exit(1);  
    }  

    // 设置一个socket地址结构server_addr,代表服务器的internet地址和端口  
    struct sockaddr_in  server_addr;  
    bzero(&server_addr, sizeof(server_addr));  
    server_addr.sin_family = AF_INET;  

    // 服务器的IP地址来自程序的参数   
    //SERVER_ADDR 指向在DOS命令行中执行程序名后的第一个字符串
    //示例：“./client 127.0.0.1“, 

    // if (inet_aton(SERVER_ADDR, &server_addr.sin_addr) == 0) 
    // //inet_aton将网络地址转成网络二进制的数字，
    // //存储到参数server_addr.sin_addr所指向的in_addr结构中
    // {  
    //     printf("Server IP Address Error!\n");  
    //     exit(1);  
    // }  

    server_addr.sin_addr.s_addr=inet_addr(SERVER_ADDR);
    server_addr.sin_port = htons(HELLO_WORLD_SERVER_PORT);  
    socklen_t server_addr_length = sizeof(server_addr);  
    //socklen_t是一种数据类型，它其实和int差不多，
    //在32位机下，size_t和int的长度相同，都是32 bits,
    //但在64位机下，size_t（32bits）和int（64 bits）的长度是不一样的,
    //socket编程中的accept函数的第三个参数的长度必须和int的长度相同。
    //于是便有了socklen_t类型，这个类型是为了增强程序的可移植性


    // 向服务器发起连接请求，连接成功后client_socket代表客户端和服务器端的一个socket连接  
    if (connect(client_socket, (struct sockaddr*)&server_addr, server_addr_length) < 0)  
    {  
        printf("Can Not Connect To %s!\n", SERVER_ADDR);  
        exit(1);  
    }  

    char file_name[FILE_NAME_MAX_SIZE + 1]=FILE_NAME;

    // // 从用户处获取文件名字
    // char file_name[FILE_NAME_MAX_SIZE + 1];  
    // bzero(file_name, sizeof(file_name));  
    // printf("Please Input File Name On Server.\t");  
    // scanf("%s", file_name);  


    //把文件名放入buffer，发送给server
    char buffer[BUFFER_SIZE];  
    bzero(buffer, sizeof(buffer));  
    strncpy(buffer, file_name, strlen(file_name) > BUFFER_SIZE ? BUFFER_SIZE : strlen(file_name));  
    // 向服务器发送buffer中的数据，此时buffer中存放的是客户端需要接收的文件的名字  
    send(client_socket, buffer, BUFFER_SIZE, 0);  

    FILE *fp = fopen(file_name, "w");  
    //w：创建一个用于写入的空文件。
    //如果文件名称与已存在的文件相同，则会删除已有文件的内容，文件被视为一个新的空文件。
    if (fp == NULL)  
    {  
        printf("File:\t%s Can Not Open To Write!\n", file_name);  
        exit(1);  
    }  

    //清空buffer
    bzero(buffer, sizeof(buffer));  

    // 从服务器端接收数据到buffer中   
    int length = 0;
    Timer time("Downloading time");  
    while(length = recv(client_socket, buffer, BUFFER_SIZE, 0)) //现在buffer被写满了
    /*recv的flags取值有：
        0： 与write()无异
        MSG_DONTROUTE:告诉内核，目标主机在本地网络，不用查路由表
        MSG_DONTWAIT:将单个I／O操作设置为非阻塞模式
        MSG_OOB:指明发送的是带外信息
    */
    {   


        int write_length = fwrite(buffer, sizeof(char), length, fp);
        //把buffer内数据通过fp写入file_name文件

        if (length < 0)  
        {  
            printf("Recieve Data From Server %s Failed!\n", SERVER_ADDR);  
            break;  
        }  
        

        if (write_length < length)  
        {  
            printf("File:\t%s Write Failed!\n", file_name);  
            break;  
        }  

        // printf("%s\n",buffer);//用来测试的

        bzero(buffer, BUFFER_SIZE); //清空buffer
    }  

    
    printf("Recieve File:\t %s From Server[%s] Finished!         ", file_name, SERVER_ADDR);  
    time.End();

    // 传输完毕，关闭socket   
    fclose(fp);  
    close(client_socket);  
    return 0;  

}  