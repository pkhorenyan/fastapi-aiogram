from fastapi import status


class TestStudents:
    """Тесты для эндпоинтов студентов"""

    def test_create_student_success(self, client, sample_student_data):
        """Тест успешного создания студента"""
        response = client.post("/students/", json=sample_student_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["first_name"] == sample_student_data["first_name"]
        assert data["last_name"] == sample_student_data["last_name"]
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_create_student_validation(self, client):
        """Тест валидации данных студента"""
        invalid_data = [
            {"first_name": "", "last_name": "Иванов"},  # пустое имя
            {"first_name": "Иван", "last_name": ""},  # пустая фамилия
            {"first_name": "A" * 51, "last_name": "Иванов"},  # слишком длинное имя
            {"first_name": "Иван", "last_name": "B" * 51},  # слишком длинная фамилия
        ]

        for data in invalid_data:
            response = client.post("/students/", json=data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_student_success(self, client, created_student):
        """Тест успешного получения студента"""
        student_id = created_student["id"]
        response = client.get(f"/students/{student_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == student_id
        assert data["first_name"] == created_student["first_name"]
        assert data["last_name"] == created_student["last_name"]

    def test_get_student_not_found(self, client):
        """Тест получения несуществующего студента"""
        response = client.get("/students/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_student_with_same_data(self, client, sample_student_data):
        """Тест создания студентов с одинаковыми данными (должно разрешаться)"""
        response1 = client.post("/students/", json=sample_student_data)
        assert response1.status_code == status.HTTP_201_CREATED

        response2 = client.post("/students/", json=sample_student_data)
        assert response2.status_code == status.HTTP_201_CREATED

        # Должны быть разные ID
        assert response1.json()["id"] != response2.json()["id"]