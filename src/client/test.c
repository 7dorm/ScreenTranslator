#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <uuid/uuid.h>

size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t total_size = size * nmemb;
    char **response_ptr = (char **)userp;

    // Allocate memory for the response and copy data
    *response_ptr = realloc(*response_ptr, strlen(*response_ptr) + total_size + 1);
    if (*response_ptr == NULL) {
        fprintf(stderr, "Realloc failed\n");
        return 0;
    }

    strncat(*response_ptr, (char *)contents, total_size);
    return total_size;
}


void handle_get(const char *url, const char *uuid) {
    CURL *curl;
    CURLcode res;

    curl = curl_easy_init();
    if (curl) {
        char full_url[256];
        snprintf(full_url, sizeof(full_url), "%s?uuid=%s", url, uuid);

        curl_easy_setopt(curl, CURLOPT_URL, full_url);
        curl_easy_setopt(curl, CURLOPT_HTTPGET, 1L);

        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "GET request failed: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }
}

void handle_post(const char *url, const char *file_path, const char *content_type, char **uuid_str) {
    CURL *curl;
    CURLcode res;

    curl = curl_easy_init();
    if (curl) {
        FILE *file = fopen(file_path, "rb");
        if (!file) {
            fprintf(stderr, "Failed to open file: %s\n", file_path);
            return;
        }

        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_READDATA, file);

        struct curl_slist *headers = NULL;
        char header[128];
        snprintf(header, sizeof(header), "Content-Type: %s", content_type);
        headers = curl_slist_append(headers, header);

        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE_LARGE, (curl_off_t)fseek(file, 0, SEEK_END));

        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "POST request failed: %s\n", curl_easy_strerror(res));
        }

        fclose(file);
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
    }
}

void handle_delete(const char *url) {
    CURL *curl;
    CURLcode res;

    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "DELETE");

        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "DELETE request failed: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }
}

int main() {
    const char *server_url = "127.0.0.1:8080";
    const char *uuid_str = "bd232054-bc35-4621-80ad-18c4cd21d1bd";
    const char *file_path = "/Users/deu/Desktop/rrefd.png";                           // Example file path
    const char *content_type = "images/jpeg";

    printf("Sending GET request...\n");
    handle_get(server_url, uuid_str);

    printf("Sending POST request...\n");
    handle_post(server_url, file_path, content_type, &uuid_str);

    printf("Sending DELETE request...\n");
    handle_delete(server_url);

    return 0;
}
