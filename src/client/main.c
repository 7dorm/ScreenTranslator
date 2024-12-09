#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h> // For the sleep function

#define MAX_COMMAND_LENGTH 512
#define MAX_INPUT_LENGTH 128
#define MAX_URL_LENGTH 128

char url[MAX_URL_LENGTH];

// Function to execute curl commands and check for errors
void execute_command(char* command) {
    int result = system(command);
    if (result != 0) {
        printf("Error executing command.\n");
    }
}

// Function to determine file type based on file extension
void determine_file_type(const char* path_to_file, char* type) {
    const char* extension = strrchr(path_to_file, '.');
    if (extension != NULL) {
        extension++; // Move past the '.'
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
            strcpy(type, "octet-stream"); // Default to a generic binary stream
        }
    }
    else {
        strcpy(type, "octet-stream"); // Default if no extension is found
    }
}

// Function to send an image
void send_image(char* path_to_file, char* uuid) {
    char type[MAX_INPUT_LENGTH];
    determine_file_type(path_to_file, type);

    char command[MAX_COMMAND_LENGTH];
    snprintf(command, sizeof(command),
        "curl -X POST -s %s -H 'Content-Type: images/%s' -T %s -o response.txt",
        url, type, path_to_file);
    execute_command(command);

    // Reading UUID from the response file
    FILE* file = fopen("response.txt", "r");
    if (file) {
        fgets(uuid, MAX_INPUT_LENGTH, file);
        printf("Received UUID: %s\n", uuid);
        fclose(file);
    }
    else {
        printf("Error: Unable to read UUID from response.\n");
    }
}

// Function to send feedback
void send_feedback(char* uuid, char* text) {
    char command[MAX_COMMAND_LENGTH];
    snprintf(command, sizeof(command),
        "curl -X PUT -s %s -H 'Content-Type: application/json' -d '{\"uuid\":\"%s\", \"text\":\"%s\"}'",
        url, uuid, text);
    execute_command(command);
}

// Function to send a GET request and check if data is received
int send_get_request(char* uuid) {
    char command[MAX_COMMAND_LENGTH];
    snprintf(command, sizeof(command),
        "curl -X GET -s '%s?uuid=%s' -H 'Content-Type: text/plain' -o response.txt",
        url, uuid);
    execute_command(command);

    // Check if response contains data
    FILE* file = fopen("response.txt", "r");
    if (file) {
        char response[MAX_INPUT_LENGTH];
        if (fgets(response, sizeof(response), file) != NULL && strlen(response) > 0) {
            printf("Server response: %s\n", response);
            fclose(file);
            return 1; // Data received
        }
        fclose(file);
    }
    return 0; // No data received
}

int main() {
    char path_to_file[MAX_INPUT_LENGTH];
    char uuid[MAX_INPUT_LENGTH];
    char text[MAX_INPUT_LENGTH];

	printf("Enter url: ");
	fgets(url, sizeof(url), stdin);
	url[strcspn(url, "\n")] = 0;

    // Get the path to the image file from the user
    printf("Enter the path to the image file: ");
    fgets(path_to_file, sizeof(path_to_file), stdin);
    path_to_file[strcspn(path_to_file, "\n")] = 0;

    while (access(path_to_file, F_OK) == -1) {
        printf("File not exist. Try again: ");
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

    // Get feedback from the user after a successful GET request
    printf("Enter feedback text: ");
    fgets(text, sizeof(text), stdin);
    text[strcspn(text, "\n")] = 0;
    // Send feedback with the UUID
    send_feedback(uuid, text);

    printf("All requests completed.\n");
    return 0;
}
