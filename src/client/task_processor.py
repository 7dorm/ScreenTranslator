import queue
import time
import random
import threading
import requests  # Для работы с HTTP-запросами

# Класс для работы с фотографиями
class Photo:
    def __init__(self, file_path, processed=False):
        self.file_path = file_path
        self.processed = processed  # Флаг, показывающий, была ли обработана фотография

    def mark_processed(self):
        self.processed = True
        print(f"Photo {self.file_path} processed.")

# Класс для работы с ИИ (пока без реальной модели)
class AIModel:
    def __init__(self):
        self.status = "Idle"
        self.result = None
        self.server_url = "http://localhost:8080/"  # URL сервера
    
    def request_model(self, photo: Photo):
        """
        Отправка фотографии на сервер для обработки.
        Здесь мы отправляем запрос через HTTP на сервер.
        """
        print(f"Sending photo {photo.file_path} for processing...")

        # Выполнение POST-запроса на сервер для отправки изображения
        with open(photo.file_path, 'rb') as file:
            files = {'file': file}
            headers = {'Content-Type': 'application/octet-stream'}
            response = requests.post(self.server_url, files=files, headers=headers)
        
        if response.status_code == 200:
            print(f"Received UUID from server: {response.text}")
            photo.mark_processed()  # Помечаем фото как обработанное
            self.status = "Completed"
            self.result = f"Processed: {photo.file_path}"
        else:
            print("Error processing photo.")
            self.status = "Error"

    def check_status(self):
        """Запрос статуса обработки модели"""
        print("Checking model status...")

        # Запрос на сервер для получения текущего статуса
        response = requests.get(f"{self.server_url}status")
        
        if response.status_code == 200:
            self.status = response.text  # Обновляем статус модели
            print(f"Model status: {self.status}")
        else:
            self.status = "Error"
            print("Error fetching model status.")

    def get_result(self):
        """Получение результата обработки"""
        if self.status == "Completed":
            return self.result
        else:
            return "Processing..."

# Класс для обработки задач (очередь)
class TaskQueue:
    def __init__(self):
        self.queue = queue.Queue()  # Очередь задач

    def add_task(self, task):
        """Добавление задачи в очередь"""
        self.queue.put(task)
    
    def process_next_task(self, ai_model: AIModel):
        """Обработка следующей задачи из очереди"""
        if not self.queue.empty():
            task = self.queue.get()
            ai_model.request_model(task)  # Отправка задачи в модель
        else:
            print("No tasks in the queue.")

# Основной процесс (например, рабочий процесс с фотографиями)
def main():
    ai_model = AIModel()  # Экземпляр ИИ модели
    task_queue = TaskQueue()  # Очередь для обработки задач

    # Добавляем фотографии в очередь
    photos = [
        Photo("photo1.jpg"),
        Photo("photo2.jpg"),
        Photo("photo3.jpg"),
    ]
    
    # Добавляем все фотографии в очередь задач
    for photo in photos:
        task_queue.add_task(photo)

    # Обрабатываем задачи
    while not task_queue.queue.empty():
        task_queue.process_next_task(ai_model)
        time.sleep(1)  # Пауза между запросами

    # Проверяем статус и выводим результаты
    while ai_model.check_status() != "Idle":
        ai_model.check_status()  # Получаем актуальный статус
        time.sleep(2)  # Пауза между проверками статуса

    print("All tasks completed.")
    print(ai_model.get_result())  # Получаем результат последней обработки

if __name__ == "__main__":
    main()
