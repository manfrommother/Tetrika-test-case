def appearance(intervals: dict[str, list[int]]) -> int:
    # Вспомогательная функция для отладки
    def debug_print_events(events):
        print("\nEvents timeline:")
        for time, event_type in events:
            event_name = {
                0: "LESSON",
                1: "PUPIL IN",
                -1: "PUPIL OUT",
                2: "TUTOR IN",
                -2: "TUTOR OUT"
            }.get(event_type, "UNKNOWN")
            print(f"Time: {time}, Event: {event_name}")

    # 1. Определяем границы урока
    lesson_start, lesson_end = intervals['lesson']

    # 2. Создаём список всех событий
    events = []
    
    # Добавляем события ученика
    for i in range(0, len(intervals['pupil']), 2):
        start = intervals['pupil'][i]
        end = intervals['pupil'][i + 1]
        if end > lesson_start and start < lesson_end:
            events.append((max(start, lesson_start), 1))   # 1 - вход ученика
            events.append((min(end, lesson_end), -1))      # -1 - выход ученика
    
    # Добавляем события учителя
    for i in range(0, len(intervals['tutor']), 2):
        start = intervals['tutor'][i]
        end = intervals['tutor'][i + 1]
        if end > lesson_start and start < lesson_end:
            events.append((max(start, lesson_start), 2))   # 2 - вход учителя
            events.append((min(end, lesson_end), -2))      # -2 - выход учителя
    
    # Если нет событий, возвращаем 0
    if not events:
        return 0
        
    # Сортируем события:
    # - Сначала по времени
    # - При равном времени: входы идут перед выходами
    # - При равном времени и типе: учитель перед учеником
    events.sort(key=lambda x: (x[0], x[1] if x[1] > 0 else 3))
    
    # debug_print_events(events)  # раскомментировать для отладки
    
    total_time = 0
    pupil_presence = 0
    tutor_presence = 0
    last_time = events[0][0]
    
    for current_time, event_type in events:
        # Если оба присутствуют, добавляем время
        if pupil_presence > 0 and tutor_presence > 0:
            total_time += current_time - last_time
        
        # Обновляем состояние присутствия
        if abs(event_type) == 1:      # Событие ученика
            pupil_presence += event_type
        elif abs(event_type) == 2:     # Событие учителя
            tutor_presence += event_type // 2
            
        last_time = current_time
    
    return total_time
