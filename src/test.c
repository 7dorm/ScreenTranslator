#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <uuid/uuid.h>

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

void handle_post(const char *url, const char *file_path, const char *content_type) {
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

void handle_put(const char *url, const char *file_path, const char *content_type) {
    CURL *curl;
    CURLcode res;

    curl = curl_easy_init();
    if (curl) {
        FILE *file = fopen(file_path, "rb");
        if (!file) {
            fprintf(stderr, "Failed to open file: %s\n", file_path);
            return;
        }

        // Calculate the file size
        fseek(file, 0, SEEK_END);
        long file_size = ftell(file);
        rewind(file); // Reset file pointer to the beginning

        // Prepare headers
        struct curl_slist *headers = NULL;
        char content_type_header[128];
        snprintf(content_type_header, sizeof(content_type_header), "Content-Type: %s", content_type);
        headers = curl_slist_append(headers, content_type_header);

        char content_length_header[128];
        snprintf(content_length_header, sizeof(content_length_header), "Content-Length: %ld", file_size);
        headers = curl_slist_append(headers, content_length_header);

        // Set CURL options
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_UPLOAD, 1L);
        curl_easy_setopt(curl, CURLOPT_READDATA, file);
        curl_easy_setopt(curl, CURLOPT_INFILESIZE_LARGE, (curl_off_t)file_size);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        // Perform the request
        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            fprintf(stderr, "PUT request failed: %s\n", curl_easy_strerror(res));
        }

        // Cleanup
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
    const char *uuid_str = "123e4567-e89b-12d3-a456-426614174000"; // Example UUID
    const char *file_path = "/Users/deu/Desktop/rrefd.png";                           // Example file path
    const char *content_type = "images/jpeg";

    printf("Sending GET request...\n");
    handle_get(server_url, uuid_str);

    printf("Sending POST request...\n");
    handle_post(server_url, file_path, content_type);

    printf("Sending PUT request...\n");
    handle_put(server_url, file_path, content_type);

    printf("Sending DELETE request...\n");
    handle_delete(server_url);

    return 0;
}
