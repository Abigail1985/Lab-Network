/*server.c*/
#include<netinet/in.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include <unistd.h> //contains various constants

#include<pthread.h>


#define HELLO_WORLD_SERVER_PORT    6666         //端口号
#define LENGTH_OF_LISTEN_QUEUE     20
#define BUFFER_SIZE                61440    //1024*60, 480kB, 
#define FILE_NAME_MAX_SIZE         512




int main(int argc, char **argv)
{
    // set socket's address information
    // 设置一个socket地址结构server_addr,代表服务器internet的地址和端口
    struct sockaddr_in   server_addr;
    bzero(&server_addr, sizeof(server_addr));//初始化
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htons(INADDR_ANY);//INADDR_ANY表示自动获取本机地址
    server_addr.sin_port = htons(HELLO_WORLD_SERVER_PORT);

    // create a stream socket
    // 创建用于internet的流协议(TCP)socket，用server_socket_doorbell代表服务器向客户端提供服务的接口
    int server_socket_doorbell = socket(PF_INET, SOCK_STREAM, 0);
    //这个FD就是File Discriptor 中文翻译为文件描述符
    //Socket起源于unix，Unix中把所有的资源都看作是文件，包括设备，比如网卡、打印机等等，
    //所以，针对Socket通信，我们在使用网卡，网卡又处理N多链接，每个链接都需要一个对应的描述，
    //也就是惟一的ID，即对应的文件描述符。
    //简单点说也就是 int fd = socket(AF_INET,SOCK_STREAM, 0); 
    //函数socket()返回的就是这个描述符。
    //在传输中我们都要使用这个惟一的ID来确定要往哪个链接上传输数据。
    if (server_socket_doorbell < 0)
    {
        printf("Create Socket Failed!\n");
        exit(1);
    }

    // 把socket和socket地址结构绑定
    if (bind(server_socket_doorbell, (struct sockaddr*)&server_addr, sizeof(server_addr)))
    {
        printf("Server Bind Port: %d Failed!\n", HELLO_WORLD_SERVER_PORT);
        exit(1);
    }

    // server_socket_doorbell用于监听
    if (listen(server_socket_doorbell, LENGTH_OF_LISTEN_QUEUE))
    {
        printf("Server Listen Failed!\n");
        exit(1);
    }

    // 服务器端一直运行用以持续为客户端提供服务
    while(1)
    {
        printf("\n\nHi,Iam running server.Listening to socket: No.%d...\n", server_socket_doorbell); 
        // 定义客户端的socket地址结构client_addr，当收到来自客户端的请求后，调用accept
        // 接受此请求，同时将client端的地址和端口等信息写入client_addr中
        struct sockaddr_in client_addr;
        socklen_t          length = sizeof(client_addr);

        // 接受一个从client端到达server端的连接请求,将客户端的信息保存在client_addr中
        // 如果没有连接请求，则一直等待直到有连接请求为止，这是accept函数的特性，可以
        // 用select()来实现超时检测
        // accpet返回一个新的socket,这个socket用来与此次连接到server的client进行通信
        // 这里的server_socket_connect代表了这个通信通道
        int server_socket_connect = accept(server_socket_doorbell, (struct sockaddr*)&client_addr, &length);
        if (server_socket_connect < 0)
        {
            printf("Server Accept Failed!\n");
            break;
        }
        printf("Successfully connect with one client with socket NO.%d...\n",server_socket_connect);

        char buffer[BUFFER_SIZE];
        bzero(buffer, sizeof(buffer));//初始化
        length = recv(server_socket_connect, buffer, BUFFER_SIZE, 0);
        //从连接门内读取数据并放入buffer，这个数据就是文件名称

        
        if (length < 0)
        {
            printf("Server Recieve Data Failed!\n");
            break;
        }

        char file_name[FILE_NAME_MAX_SIZE + 1];//file_name从client处获取
        bzero(file_name, sizeof(file_name));
        strncpy(file_name, buffer,
                strlen(buffer) > FILE_NAME_MAX_SIZE ? FILE_NAME_MAX_SIZE : strlen(buffer));
                //式A?B:C值为：若A为真,则B；若A为假,则C。

        FILE *fp = fopen(file_name, "r");//r：打开一个用于读取的文件。该文件必须存在。
        if (fp == NULL)
        {
            printf("File:\t%s Not Found!\n", file_name);
        }
        else
        {
            bzero(buffer, BUFFER_SIZE);
            int file_block_length = 0;
            while( (file_block_length = fread(buffer, sizeof(char), BUFFER_SIZE, fp)) > 0)
            //从给定流 stream 读取数据到 buffer 所指向的数组中，
            //sizeof(char)是要读取的每个元素的大小，以字节为单位
            //BUFFER_SIZE是元素的个数
            //fp是一个指向FILE对象的指针，该对象指定了一个输入流

            {
                printf("file_block_length = %d\n", file_block_length);

                // 发送buffer中的字符串到server_socket_connect,实际上就是发送给客户端
                if (send(server_socket_connect, buffer, file_block_length, 0) < 0)
                //因为传输失败的话返回值是-1而不是0
                {
                    printf("Send File:\t%s Failed!\n", file_name);
                    break;
                }

                bzero(buffer, sizeof(buffer));//重新初始化buffer
            }
            fclose(fp);
            printf("File:\t%s Transfer Finished!\n", file_name);
        }

        close(server_socket_connect);
    }

    close(server_socket_doorbell);

    return 0;
}
