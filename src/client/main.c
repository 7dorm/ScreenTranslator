#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_COMMAND_LENGTH 512
#define MAX_INPUT_LENGTH 128

// Функция для выполнения curl-запросов и получения ответа
void execute_command(char* command) {
    int result = system(command);
    if (result != 0) {
        printf("Error executing command.\n");
    }
}

// Функция для отправки изображения
void send_image(char* type, char* path_to_file, char* uuid) {

    char command[MAX_COMMAND_LENGTH];
    snprintf(command, sizeof(command),
        "curl -X POST -s http://localhost:8080/ -H 'Content-Type: images/%s' -T %s -o response.txt",
        type, path_to_file);
    execute_command(command);

    // Чтение UUID из файла response.txt
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

// Функция для отправки отзыва
void send_feedback(char* uuid, char* text) {
    char command[MAX_COMMAND_LENGTH];
    snprintf(command, sizeof(command),
        "curl -X PUT -s http://localhost:8080/ -H 'Content-Type: application/json' -d '{\"uuid\":\"%s\", \"text\":\"%s\"}'",
        uuid, text);
    execute_command(command);
}

// Функция для отправки GET-запроса с сообщением
void send_get_request(char* message) {
    char command[MAX_COMMAND_LENGTH];
    snprintf(command, sizeof(command),
        "curl -X GET -s 'http://localhost:8080/?message=%s' -H 'Content-Type: text/plain'",
        message);
    execute_command(command);// wait for responce
}

int main() {
    char type[MAX_INPUT_LENGTH];
    char path_to_file[MAX_INPUT_LENGTH];
    char uuid[MAX_INPUT_LENGTH];
    char text[MAX_INPUT_LENGTH];
    char message[MAX_INPUT_LENGTH];

    // Запрос пути к изображению и типа
    printf("Enter the file type of the image (e.g., jpeg, png): "); // remove this
    fgets(type, sizeof(type), stdin);
    type[strcspn(type, "\n")] = 0;

    printf("Enter the path to the image file: ");
    fgets(path_to_file, sizeof(path_to_file), stdin);
    path_to_file[strcspn(path_to_file, "\n")] = 0;

    // Отправка изображения и получение UUID
    send_image(type, path_to_file, uuid);

    // Запрос отзыва
    printf("Enter feedback text: ");
    fgets(text, sizeof(text), stdin);
    text[strcspn(text, "\n")] = 0;

    // Отправка отзыва с UUID
    send_feedback(uuid, text);

    // Запрос сообщения для GET-запроса
    printf("Enter a message for the GET request: ");
    fgets(message, sizeof(message), stdin);
    message[strcspn(message, "\n")] = 0;

    // Отправка GET-запроса
    send_get_request(message);

    printf("All requests completed.\n");
    return 0;
}