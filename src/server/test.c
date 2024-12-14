#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

// Callback to handle server responses
size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t total_size = size * nmemb;
    char **response_ptr = (char **)userp;

    *response_ptr = realloc(*response_ptr, strlen(*response_ptr) + total_size + 1);
    if (*response_ptr == NULL) {
        fprintf(stderr, "Realloc failed\n");
        return 0;
    }

    strncat(*response_ptr, (char *)contents, total_size);
    return total_size;
}

// Function to perform HTTP GET
void perform_get(const char *url) {
    CURL *curl = curl_easy_init();
    char *response = calloc(1, sizeof(char));
    if (!response) {
        fprintf(stderr, "Memory allocation failed\n");
        return;
    }

    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

        CURLcode res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            printf("GET Response: %s\n", response);
        } else {
            fprintf(stderr, "GET failed: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }
    free(response);
}

// Function to perform HTTP POST with binary data
void perform_post(const char *url, const char *file_path) {
    CURL *curl = curl_easy_init();
    FILE *file = fopen(file_path, "rb");
    char *response = calloc(1, sizeof(char));
    if (!response) {
        fprintf(stderr, "Memory allocation failed\n");
        return;
    }

    if (file && curl) {
        // Get the file size
        fseek(file, 0, SEEK_END);
        long file_size = ftell(file);
        rewind(file);

        char *file_data = malloc(file_size);
        if (!file_data) {
            fprintf(stderr, "Memory allocation failed\n");
            fclose(file);
            return;
        }
        fread(file_data, 1, file_size, file);
        fclose(file);

        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, file_data);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, file_size);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

        CURLcode res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            printf("POST Response: %s\n", response);
        } else {
            fprintf(stderr, "POST failed: %s\n", curl_easy_strerror(res));
        }

        free(file_data);
        curl_easy_cleanup(curl);
    } else {
        fprintf(stderr, "Failed to open file or initialize CURL\n");
    }
    free(response);
}

// Function to perform HTTP PUT
void perform_put(const char *url) {
    CURL *curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "PUT");

        CURLcode res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            printf("PUT request sent successfully\n");
        } else {
            fprintf(stderr, "PUT failed: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }
}

// Function to perform HTTP DELETE
void perform_delete(const char *url) {
    CURL *curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "DELETE");

        CURLcode res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            printf("DELETE request sent successfully\n");
        } else {
            fprintf(stderr, "DELETE failed: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }
}

int main() {
    const char *server_url = "127.0.0.1:8000"; // Update with your server's address
    const char *image_path = "/Users/deu/Desktop/rrefd.png";            // Replace with the path to your image

	printf("\nPerforming POST request with image...\n");
    perform_post(server_url, image_path);

    printf("Performing GET request...\n");
    perform_get(server_url);

    printf("\nPerforming PUT request...\n");
    perform_put(server_url);

    printf("\nPerforming DELETE request...\n");
    perform_delete(server_url);

    return 0;
}
