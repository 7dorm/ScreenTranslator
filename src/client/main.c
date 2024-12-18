#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

// Function to handle data received from server
size_t write_callback(char *ptr, size_t size, size_t nmemb, void *userdata) {
    return size * nmemb;
}

char *get_file_type(const char *filename) {
    const char *dot = strrchr(filename, '.');
    if(dot != NULL && dot != filename) {
        return &dot[1];
    } else {
        return "unknown";
    }
}

size_t get_content_length(const char *file_path) {
    FILE *fp = fopen(file_path, "rb");
    if (fp == NULL) {
        printf("Failed to open file: %s\n", file_path);
        return 0;
    }

    fseek(fp, 0, SEEK_END);
    size_t content_length = ftell(fp);

    fclose(fp);
    return content_length;
}

int get_request(const char *url) {
    CURL *curl;
    CURLcode res;

    // Initialize curl library
    curl_global_init(CURL_GLOBAL_DEFAULT);

    // Create a new curl session
    curl = curl_easy_init();
    if(curl == NULL) {
        printf("Failed to initialize curl\n");
        return 1;
    }

    // Set URL for GET request
    curl_easy_setopt(curl, CURLOPT_URL, url);

    // Send GET request and retrieve response code
    res = curl_easy_perform(curl);
    if(res != CURLE_OK) {
        printf("GET request failed: %s\n", curl_easy_strerror(res));
        return 1;
    } else {
        long status_code;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status_code);
        printf("GET response code: %ld\n", status_code);

        // Clean up
        curl_easy_cleanup(curl);
        curl_global_cleanup();
        return 0;
    }
}


// curl -X POST -v http://localhost:8080/ -H 'Content-Type: images/{type}' -T {path_to_file}"
int post_request(const char *url, const char *data) {
    CURL *curl;
    CURLcode res;

    curl_global_init(CURL_GLOBAL_DEFAULT);

    curl = curl_easy_init();
    if(curl == NULL) {
        printf("Failed to initialize curl\n");
        return 1;
    }

    char *content_types = "Content-Type: images/%s";
    char *file_type = get_file_type(data);

    char *result = calloc((strlen(file_type)+strlen(content_types))+1, sizeof(char));
    snprintf(result, sizeof(char)*(strlen(file_type)+strlen(content_types)), content_types, file_type);
    
    
    printf("%s\n", result);

    char *content_length = "Content-Length: %d";
    char *result2 = calloc(sizeof(content_length) + 8, sizeof(char));
    snprintf(result2, sizeof(char)*(strlen(content_length) + 8), content_length, get_content_length(data));
    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, result);
    headers = curl_slist_append(headers, result2);
    free(result);
    free(result2);
    // headers = curl_slist_append(headers, "filename: example.txt");
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_UPLOAD, 1L);
    curl_easy_setopt(curl, CURLOPT_READDATA, data);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    printf("Test\n");
    // Send POST request and retrieve response code
    res = curl_easy_perform(curl);
    printf("test\n");

    long status_code;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status_code);
    printf("POST response code: %ld\n", status_code);
    if(res != CURLE_OK) {
        printf("POST request failed: %s\n", curl_easy_strerror(res));
        return 1;
    } else {
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
        curl_global_cleanup();
        return 0;
    }
}

int main() {
    const char *get_url = "http://localhost:8080";
    const char *post_url = "http://localhost:8080";
    const char *post_data = "/Users/deu/Desktop/rrefd.png";

    // Send GET request
    // if(get_request(get_url) != 0) {
    //     printf("GET request failed\n");
    //     return 1;
    // }

    // Send POST request
    if(post_request(post_url, post_data) != 0) {
        printf("POST request failed\n");
        return 1;
    }

    return 0;
}