#include <stdio.h>
#include <curl/curl.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#define MAX_URL_SIZE 128
#define MAX_COMMAND_LENGTH 512
#define MAX_INPUT_LENGTH 128

void perform_request(const char *url, const char *method, const char *data) {
    CURL *curl;
    CURLcode res;
    long status_code;

    // Initialize libcurl
    curl = curl_easy_init();
    if (curl) {
        // Set the URL
        curl_easy_setopt(curl, CURLOPT_URL, url);

        // Configure HTTP methods
        if (strcmp(method, "POST") == 0) {
            curl_easy_setopt(curl, CURLOPT_POST, 1L);
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
        } else if (strcmp(method, "PUT") == 0) {
            curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "PUT");
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
        } else if (strcmp(method, "DELETE") == 0) {
            curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "DELETE");
        }

        // Optionally follow redirects
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);

        // Perform the request
        res = curl_easy_perform(curl);

        if (res == CURLE_OK) {
            // Get the response status code
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status_code);
            printf("%s request to %s returned status code: %ld\n", method, url, status_code);
        } else {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }

        // Clean up
        curl_easy_cleanup(curl);
    } else {
        fprintf(stderr, "Failed to initialize CURL.\n");
    }
}


int main(void) {
	char url[MAX_URL_SIZE] = {0};
	char path_to_file[MAX_INPUT_LENGTH] = {0};
	char uuid[MAX_INPUT_LENGTH] = {0};
	char text[MAX_INPUT_LENGTH] = {0};
	
	printf("Enter url: ");
	fgets(url, MAX_URL_SIZE, stdin);
	url[strcspn(url, "\n")] = 0;
			
	printf("Enter the path to the image file: ");
	fgets(path_to_file, sizeof(path_to_file), stdin);
	path_to_file[strcspn(path_to_file, "\n")] = 0;
	
	while (access(path_to_file, F_OK) == -1) {
	    printf("File not exist. Try again: ");
	    fgets(path_to_file, sizeof(path_to_file), stdin);
	    path_to_file[strcspn(path_to_file, "\n")] = 0;
	}
	
	perform_request(url, "POST", )
    return 0;
}
