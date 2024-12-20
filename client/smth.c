#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h> // For sleep function
#include <curl/curl.h>

#define MAX_INPUT_LENGTH 128
#define MAX_URL_LENGTH 128

char url[MAX_URL_LENGTH];

// Callback function to capture response data
size_t write_callback(void* contents, size_t size, size_t nmemb, void* userp) {
    size_t total_size = size * nmemb;
    strncat((char*)userp, (char*)contents, total_size);
    return total_size;
}

// Function to determine file type based on file extension
void determine_file_type(const char* path_to_file, char* type) {
    const char* extension = strrchr(path_to_file, '.');
    if (extension) {
        extension++; // Skip the dot
        if (strcmp(extension, "jpeg") == 0 || strcmp(extension, "jpg") == 0) {
            strcpy(type, "jpeg");
        }
        else if (strcmp(extension, "png") == 0) {
            strcpy(type, "png");
        }
        else if (strcmp(extension, "gif") == 0) {
            strcpy(type, "gif");
        }
        else if (strcmp(extension, "bmp") == 0) {
            strcpy(type, "bmp");
        }
        else {
            strcpy(type, "octet-stream"); // Default type
        }
    }
    else {
        strcpy(type, "octet-stream"); // Default if no extension
    }
}

// Function to send an image and get the UUID
void send_image(const char* path_to_file, char* uuid) {
    CURL* curl;
    CURLcode res;
    FILE* file;
    char type[MAX_INPUT_LENGTH];
    char response[512] = "";

    determine_file_type(path_to_file, type);

    file = fopen(path_to_file, "rb");
    if (!file) {
        fprintf(stderr, "Error opening file: %s\n", path_to_file);
        return;
    }

    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_UPLOAD, 1L);
        curl_easy_setopt(curl, CURLOPT_READDATA, file);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, response);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, curl_slist_append(NULL, "Content-Type: image/jpeg"));

        res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            printf("Image uploaded successfully.\nResponse: %s\n", response);
            strncpy(uuid, response, MAX_INPUT_LENGTH - 1);
        }
        else {
            fprintf(stderr, "Error sending image: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }

    fclose(file);
}

// Function to send feedback
void send_feedback(const char* uuid, const char* text) {
    CURL* curl;
    CURLcode res;
    char json_data[MAX_INPUT_LENGTH];
    char response[512] = "";

    snprintf(json_data, sizeof(json_data), "{\"uuid\":\"%s\", \"text\":\"%s\"}", uuid, text);

    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "PUT");
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_data);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, response);

        res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            printf("Feedback sent successfully.\nResponse: %s\n", response);
        }
        else {
            fprintf(stderr, "Error sending feedback: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }
}

// Function to send a GET request and check if data is received
int send_get_request(const char* uuid) {
    CURL* curl;
    CURLcode res;
    char full_url[MAX_URL_LENGTH + MAX_INPUT_LENGTH];
    char response[512] = "";

    snprintf(full_url, sizeof(full_url), "%s?uuid=%s", url, uuid);

    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, full_url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, response);

            res = curl_easy_perform(curl);
        if (res == CURLE_OK && strlen(response) > 0) {
            printf("Server response: %s\n", response);
            curl_easy_cleanup(curl);
            return 1; // Data received
        }

        curl_easy_cleanup(curl);
    }

    return 0; // No data received
}

int main() {
    char path_to_file[MAX_INPUT_LENGTH];
    char uuid[MAX_INPUT_LENGTH];
    char text[MAX_INPUT_LENGTH];

    printf("Enter URL: ");
    fgets(url, sizeof(url), stdin);
    url[strcspn(url, "\n")] = 0;

    printf("Enter the path to the image file: ");
    fgets(path_to_file, sizeof(path_to_file), stdin);
    path_to_file[strcspn(path_to_file, "\n")] = 0;

    while (access(path_to_file, F_OK) == -1) {
        printf("File not found. Try again: ");
        fgets(path_to_file, sizeof(path_to_file), stdin);
        path_to_file[strcspn(path_to_file, "\n")] = 0;
    }

    // Send the image and get the UUID
    send_image(path_to_file, uuid);

    // Continuously send GET requests until data is received
    while (!send_get_request(uuid)) {
        printf("No data received. Retrying...\n");
        sleep(2); // Wait before retrying
    }

    // Get feedback from the user
    printf("Enter feedback text: ");
    fgets(text, sizeof(text), stdin);
    text[strcspn(text, "\n")] = 0;

    // Send feedback with the UUID
    send_feedback(uuid, text);

    printf("All requests completed.\n");
    return 0;
}