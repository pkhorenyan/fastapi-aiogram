import pytest
from fastapi import status


class TestIntegration:
    """Интеграционные тесты полного сценария"""

    def test_full_student_flow(self, client):
        """Полный тест сценария: создание студента → добавление баллов → просмотр"""
        # 1. Создаем студента
        student_data = {"first_name": "Петр", "last_name": "Петров"}
        create_response = client.post("/students/", json=student_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        student = create_response.json()
        student_id = student["id"]

        # 2. Добавляем несколько баллов
        scores_data = [
            {"subject": "Математика", "score": 85},
            {"subject": "Русский язык", "score": 92},
            {"subject": "Физика", "score": 78},
        ]

        for score_data in scores_data:
            response = client.post(f"/students/{student_id}/scores/", json=score_data)
            assert response.status_code == status.HTTP_200_OK

        # 3. Обновляем один балл
        update_response = client.post(
            f"/students/{student_id}/scores/",
            json={"subject": "Математика", "score": 90}
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["score"] == 90

        # 4. Получаем студента и проверяем данные
        student_response = client.get(f"/students/{student_id}")
        assert student_response.status_code == status.HTTP_200_OK
        student_data = student_response.json()

        assert student_data["first_name"] == "Петр"
        assert student_data["last_name"] == "Петров"

        # 5. Получаем все баллы студента
        scores_response = client.get(f"/students/{student_id}/scores/")
        assert scores_response.status_code == status.HTTP_200_OK
        scores = scores_response.json()

        assert len(scores) == 3  # 3 предмета

        # Проверяем, что математика обновилась
        math_score = next(score for score in scores if score["subject"] == "Математика")
        assert math_score["score"] == 90

    def test_multiple_students_scores(self, client):
        """Тест работы с несколькими студентами и их баллами"""
        # Создаем двух студентов
        student1 = client.post("/students/", json={"first_name": "Анна", "last_name": "Сидорова"}).json()
        student2 = client.post("/students/", json={"first_name": "Мария", "last_name": "Кузнецова"}).json()

        # Добавляем баллы разным студентам
        client.post(f"/students/{student1['id']}/scores/", json={"subject": "Математика", "score": 85})
        client.post(f"/students/{student2['id']}/scores/", json={"subject": "Математика", "score": 92})

        # Проверяем, что баллы не смешиваются
        scores1 = client.get(f"/students/{student1['id']}/scores/").json()
        scores2 = client.get(f"/students/{student2['id']}/scores/").json()

        assert len(scores1) == 1
        assert len(scores2) == 1
        assert scores1[0]["score"] == 85
        assert scores2[0]["score"] == 92