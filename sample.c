/* f20170670@hyderabad.bits-pilani.ac.in - Devendra Dheeraj Gupta Sanagapalli */

/* This program works similar to a web-scraper. It opens socket on a given proxy server. Once the connection
* (or basically an webpage which has a PNG image embedded in it), the retrieved HTML file is parsed and the
*	URL in the IMG SRC tag is established, the webpage HTML is retrieved through the socket and is stored in
* .html file. To retrieve the image from google extracted and the PNG image is read in bytes. Once the received
* bytes are stored in a .gif file, the program closes all open streams and sockets and terminates normally.
*/

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>

#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>
#include <stdio.h>

typedef unsigned char byte;
byte alphabet[]=
"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
"abcdefghijklmnopqrstuvwxyz"
"0123456789+/";

byte *to_base64(byte data[], int size){
	byte *b64 = (byte *)malloc(100 * sizeof(byte));
	memset(b64,0,sizeof(b64));
	int i=0;
	for(;i<size;i++)
	{
		byte b=data[i];
		byte c1=b>>2;
		sprintf(b64, "%s%c", b64, alphabet[c1]);
		byte c2=b<<6;
		c2=c2>>2;
		i++;
		if(i>=size){
		sprintf(b64, "%s%c", b64, alphabet[c2]);
			break;
		}
		byte bb=data[i];
		byte c3=bb>>4;
		c2+=c3;
		sprintf(b64, "%s%c", b64, alphabet[c2]);
		byte c4=bb<<4;
		c4=c4>>2;
		i++;
		if(i>=size){
		sprintf(b64, "%s%c", b64, alphabet[c4]);
			break;
		}
		byte bbb=data[i];
		byte c5=bbb>>6;
		c4+=c5;
		sprintf(b64, "%s%c", b64, alphabet[c4]);
		byte c6=bbb<<2;
		c6=c6>>2;
		sprintf(b64, "%s%c", b64, alphabet[c6]);
	}
	if(strlen(b64)%4!=0)sprintf (b64, "%s%c", b64, '=');
	if(strlen(b64)%4!=0)sprintf (b64, "%s%c", b64, '=');

	return b64;
}

int main(int argc, char *argv[]){

  char* website = argv[1];
  char* username = argv[4];
  char* password = argv[5];
  char* htmlfilename = argv[6];
  char* logofilename = argv[7];
	char creds[1024];
	char htmlReq[1024];
	int found30x = 1;

	snprintf(creds, 1024, "%s:%s", username, password);
  char* encodedCreds = to_base64(creds, strlen(creds));
	char imageurl[1024];

  snprintf(htmlReq,1024,"GET http://%s/ HTTP/1.1\r\nHost: %s\r\n"
	                       "Connection: close\r\nAccept: text/html\r\n"
	                       "Proxy-Authorization: Basic %s\r\n\r\n",website, website, encodedCreds);
	int count =1;	int ind=0;
	while(found30x){
		// printf("%d\n", count++);
		printf("%s\n", htmlReq);
		FILE *fp;
		fp = fopen(htmlfilename,"w+");
		int bytes_read;
		char server_reply[1024];
		char redirecturl[1024];
		ind = 0;

		// Connection to proxy.
		int proxy_socket;
		struct sockaddr_in proxy_server;
		if((proxy_socket=socket(AF_INET, SOCK_STREAM,0))<0){ printf("Error in creating proxy socket\n");return 1;}
		memset(&proxy_server,'0',sizeof(proxy_server));
		proxy_server.sin_addr.s_addr = inet_addr(argv[2]); //argv[2] = ip address of proxy
		proxy_server.sin_family = AF_INET;
		proxy_server.sin_port = htons(atoi(argv[3])); //argv[3] = port number of proxy

		if(connect(proxy_socket, (struct sockaddr*)&proxy_server, sizeof(proxy_server))<0){
			puts("Error in connecting to proxy");
			return 1;
		}
		// puts("Connection Successfull\n");
		// --------- PROXY CONNECTION SUCCESSFULL ----------//

		found30x = 0;
		// printf("\n%d-\n", count++);
	  // puts(htmlReq);
		if(send(proxy_socket, htmlReq, strlen(htmlReq), 0) < 0 ){
			puts("Html ssend req failed\n");
			return 1;
		}
	  // puts("Html req sent!\n");

	  do {
	      bytes_read = read(proxy_socket, server_reply, sizeof(server_reply));
	      server_reply[bytes_read]=0;
				// fputs(server_reply, stdout);

				// ----- CHECK FOR HTTP 30x RESPONSE ----- //
				char *check30x = strstr(server_reply,"HTTP/1.1 30");
				if(check30x != NULL){
					found30x = 1;
					check30x = strstr(server_reply,"Location: ");
					if(check30x != NULL){
						check30x += strlen("Location: ");
						while(check30x[0] != '\r'){
							redirecturl[ind++] = check30x[0];
							check30x++;
						}
						redirecturl[ind] = '\0';
						ind = 0;
					}
					break;
				}

				// ----- CHECK FOR HTTP RESPONSE END ---- //
	      char *content = strstr(server_reply,"Connection: close\r\n\r\n");
	      if(content != NULL) content += 21;
	      else content = server_reply;
				fputs(content, fp);

				// PARSING server_reply FOR IMAGE TAG
				if(ind == 0 && strcmp(website,"info.in2p3.fr")==0){
						char *imagetag = strstr(server_reply, "<IMG SRC=");
						if(imagetag != NULL && ind != 1024) {
							imagetag += strlen("<img src=") + 1;
							while(imagetag[0] != '"'){
								if(ind != -1) imageurl[ind++] = imagetag[0];
								imagetag++;
							}
							imageurl[ind] = '\0';
							ind = 1024;
						}
				}
	      memset(server_reply, 0, sizeof(server_reply));
	  } while (bytes_read > 0);

		// Send_Request.!!!
		if (found30x){
			char* host;
			host = (char *)malloc(100 * sizeof(char));
			int index=0;
			char *httpcheck = strstr(redirecturl,"http://");
			if(httpcheck != NULL){
				// ABSOLUTE PATH
				httpcheck += strlen("http://");
				while(httpcheck[0] != '/' && httpcheck[0] != '\0'){
					host[index++] = httpcheck[0];
					httpcheck++;
				}
				host[index] = '\0';
				// printf("Host is %s\n", host);
				snprintf(htmlReq,BUFSIZ,"GET %s HTTP/1.1\r\nHost: %s\r\n"
	                       "Connection: close\r\nAccept: text/html\r\n"
	                       "Proxy-Authorization: Basic %s\r\n\r\n",redirecturl, host, encodedCreds);

			}else{
				while(httpcheck[0] != '/' && httpcheck[0] != '\0'){
					host[index++] = httpcheck[0];
					httpcheck++;
				}
				host[index] = '\0';
				// if(strlen(host) == 0){
				// 	strcpy(host, website);
				// }
				snprintf(htmlReq,BUFSIZ,"GET http://%s HTTP/1.1\r\nHost: %s\r\n"
	                       "Connection: close\r\nAccept: text/html\r\n"
	                       "Proxy-Authorization: Basic %s\r\n\r\n",redirecturl, host, encodedCreds);
			}
		}
		fclose(fp);
		close(proxy_socket);
	}

  // puts("Reply recieved!");
	// -------------- HTML and IMAGE URL DOWNLOADED --------------//
	// printf("Image url is : %s\n", imageurl);
	if(strcmp(website,"info.in2p3.fr")==0){
		int image_proxy_socket;
		if((image_proxy_socket=socket(AF_INET, SOCK_STREAM,0))<0){
			printf("Error in creating image proxy socket\n");
			return 1;
		}
		struct sockaddr_in image_proxy_server;
		memset(&image_proxy_server,'0',sizeof(image_proxy_server));
		image_proxy_server.sin_addr.s_addr = inet_addr(argv[2]); //argv[2] = ip address of proxy
		image_proxy_server.sin_family = AF_INET;
		image_proxy_server.sin_port = htons(atoi(argv[3])); //argv[3] = port number of proxy

		if(connect(image_proxy_socket, (struct sockaddr*)&image_proxy_server, sizeof(image_proxy_server))<0){
			puts("Error in connecting to proxy");
			return 1;
		}
		// puts("Image Server and Image socket connection successfull\n");
		char imageReq[1024];
		snprintf(imageReq,BUFSIZ,"GET http://%s/%s HTTP/1.1\r\nHost: %s\r\n"
														 "Connection: close\r\n"
														 "Proxy-Authorization: Basic %s\r\n\r\n",website, imageurl, website, encodedCreds);

		// puts(imageReq);

		if(send(image_proxy_socket, imageReq, strlen(imageReq), 0) < 0 ){
			puts("Image ssend req failed\n");
			return 1;
		}

		// puts("Image req sent!\n");

		FILE *image_fp = fopen(logofilename, "wb");
		int image_bytes_read, total=0,len;
		byte image_server_reply[418];
		char length[100];
		ind = 0;

		image_bytes_read = recv(image_proxy_socket, image_server_reply, sizeof(image_server_reply), 0);
		// printf("Read %d bytes of data\n", image_bytes_read );
		// puts(image_server_reply);
		byte *content_length = strstr(image_server_reply,"Content-Length: ");
		if(content_length != NULL){
			content_length += strlen("Content-Length: ");
			while(content_length[0] != '\r'){
				length[ind++] = content_length[0];
				content_length++;
			}
			length[ind] = '\0';
			len = atoi(length);
		}
		fflush(image_fp);
		while(len > 0){
			// printf("%s\n", "Writing to file");
			image_bytes_read = read(image_proxy_socket, image_server_reply, sizeof(image_server_reply));
			fwrite(image_server_reply, 1, image_bytes_read, image_fp);
			len -= image_bytes_read;
			memset(image_server_reply,0,sizeof(image_server_reply));
			fflush(image_fp);
		}
		fclose(image_fp);
		close(image_proxy_socket);
	}
	// puts("Image downloaded!");
  return 0;
}
