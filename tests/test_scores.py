from fastapi import status


class TestScores:
    """Тесты для эндпоинтов баллов"""

    def test_upsert_score_create_success(self, client, created_student, sample_score_data):
        """Тест успешного создания балла"""
        student_id = created_student["id"]
        response = client.post(f"/students/{student_id}/scores/", json=sample_score_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["subject"] == sample_score_data["subject"]
        assert data["score"] == sample_score_data["score"]
        assert data["student_id"] == student_id
        assert "id" in data

    def test_upsert_score_update_success(self, client, created_student, sample_score_data):
        """Тест успешного обновления балла"""
        student_id = created_student["id"]

        # Создаем первый балл
        response1 = client.post(f"/students/{student_id}/scores/", json=sample_score_data)
        assert response1.status_code == status.HTTP_200_OK
        original_score = response1.json()["score"]

        # Обновляем балл
        updated_data = sample_score_data.copy()
        updated_data["score"] = 95
        response2 = client.post(f"/students/{student_id}/scores/", json=updated_data)

        assert response2.status_code == status.HTTP_200_OK
        data = response2.json()

        assert data["subject"] == sample_score_data["subject"]
        assert data["score"] == 95  # обновленное значение
        assert data["score"] != original_score

    def test_upsert_score_validation(self, client, created_student):
        """Тест валидации баллов"""
        student_id = created_student["id"]
        invalid_scores = [
            {"subject": "Математика", "score": -1},  # отрицательный балл
            {"subject": "Математика", "score": 101},  # балл больше 100
            {"subject": "", "score": 85},  # пустой предмет
            {"subject": "A" * 51, "score": 85},  # слишком длинный предмет
        ]

        for data in invalid_scores:
            response = client.post(f"/students/{student_id}/scores/", json=data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_upsert_score_student_not_found(self, client, sample_score_data):
        """Тест добавления балла несуществующему студенту"""
        response = client.post("/students/999/scores/", json=sample_score_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_scores_success(self, client, created_student, sample_score_data):
        """Тест успешного получения списка баллов"""
        student_id = created_student["id"]

        # Добавляем несколько баллов
        subjects = ["Математика", "Русский язык", "Физика"]
        for subject in subjects:
            score_data = sample_score_data.copy()
            score_data["subject"] = subject
            client.post(f"/students/{student_id}/scores/", json=score_data)

        # Получаем список баллов
        response = client.get(f"/students/{student_id}/scores/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == len(subjects)
        returned_subjects = [score["subject"] for score in data]
        for subject in subjects:
            assert subject in returned_subjects

    def test_list_scores_empty(self, client, created_student):
        """Тест получения пустого списка баллов"""
        student_id = created_student["id"]
        response = client.get(f"/students/{student_id}/scores/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_scores_student_not_found(self, client):
        """Тест получения баллов несуществующего студента"""
        response = client.get("/students/999/scores/")
        assert response.status_code == status.HTTP_404_NOT_FOUND