import io
import json
from collections import Counter
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
import requests
import csv
from .models import AnswerRecord, SurveyResponse
import logging

# Configure logging
logger = logging.getLogger(__name__)

def index(request):
    # API endpoints (replace with your actual API endpoint if needed)
    urls = [
        "https://services.api.unity.com/cloud-save/v1/data/projects/77f104be-1501-4cb5-b939-e690de43ec34/environments/002f4514-3bea-412a-a9dc-37e1ba68de0f/players/ynntMpW2Ft7WndUE9hwjg8wySbQ4/items",
    ]
    
    auth_header = "Basic MDgwMTMzNzktMzdlMy00YzE1LTk4ZjQtYjVjZWE2MmU4NmVhOlJBVUxUWFhwdHM2V3ZTR3ZCVVhVVW1zMXNkb2h2b3VP"

    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }

    # Correct answers for technical questions (Q6–Q15, Q26–Q30)
    correct_answers = [
        [1],  # Q6: B - Hyper Text Markup Language
        [2],  # Q7: C - X$9!q@T#nP
        [1],  # Q8: B - False
        [2],  # Q9: C - Array
        [1],  # Q10: B - 32
        [1],  # Q11: B - Social engineering attack
        [2],  # Q12: C - Artificial Intelligence
        [2],  # Q13: C - Excel
        [0],  # Q14: A - Repeating actions
        [1],  # Q15: B - False
        [1],  # Q26: B - Teaching computers to learn
        [2],  # Q27: C - Network protection
        [1],  # Q28: B - 14
        [1],  # Q29: B - Data
        [0],  # Q30: A - Cybersecurity
    ]

    key_value_pairs = {}

    def compare_answers(user_answer, correct_answer):
        if len(user_answer) == 1 and len(correct_answer) == 1:
            return user_answer == correct_answer
        else:
            user_set = set(user_answer)
            correct_set = set(correct_answer)
            valid_numbers = {0, 1, 2, 3}
            return user_set == correct_set and all(x in valid_numbers for x in user_set)

    def recommend_course(survey_answers, quiz_answers, correctness):
        # Initialize scores for each course
        computing_score = 0
        cybersecurity_score = 0
        ai_score = 0

        # Interest & Aspiration (Q1–Q5)
        for i, answer in enumerate(survey_answers[:5], 1):
            if answer:
                choice = answer[0] if isinstance(answer, list) else answer
                if i == 1:  # Career preference
                    if choice == 0: computing_score += 2
                    elif choice == 1: cybersecurity_score += 2
                    elif choice == 2: ai_score += 2
                elif i == 2:  # Task preference
                    if choice == 2: computing_score += 2
                    elif choice == 0: cybersecurity_score += 2
                    elif choice == 1: ai_score += 2
                elif i == 3:  # Project role
                    if choice == 0: computing_score += 2
                    elif choice == 1: cybersecurity_score += 2
                    elif choice == 2: ai_score += 2
                elif i == 4:  # Excitement
                    if choice == 1: cybersecurity_score += 2
                    elif choice == 0: ai_score += 2
                    elif choice == 2: computing_score += 2
                elif i == 5:  # Topic to explore
                    if choice == 2: ai_score += 2
                    elif choice == 0: cybersecurity_score += 2
                    elif choice == 1: computing_score += 2

        # Technical Aptitude (Q6–Q15, Q26–Q30)
        computing_questions = [6, 9, 13, 14]
        cybersecurity_questions = [7, 11, 27, 30]
        ai_questions = [8, 10, 12, 15, 26, 28, 29]

        for i, correct in enumerate(correctness, 6):
            if correct:
                if i in computing_questions:
                    computing_score += 3
                elif i in cybersecurity_questions:
                    cybersecurity_score += 3
                elif i in ai_questions:
                    ai_score += 3

        # Personality & Work Style (Q16–Q20)
        for i, answer in enumerate(survey_answers[5:10], 16):
            if answer:
                choice = answer[0] if isinstance(answer, list) else answer
                if i == 16:  # Work preference
                    if choice == 2: computing_score += 1
                    elif choice == 1: cybersecurity_score += 1
                    elif choice == 0: ai_score += 1
                elif i == 17:  # Error handling
                    if choice == 0: computing_score += 1
                    elif choice == 2: cybersecurity_score += 1
                    elif choice == 1: ai_score += 1
                elif i == 18:  # Self-description
                    if choice == 2: computing_score += 1
                    elif choice == 1: cybersecurity_score += 1
                    elif choice == 0: ai_score += 1
                elif i == 19:  # Learning preference
                    if choice == 1: computing_score += 1
                    elif choice == 2: cybersecurity_score += 1
                    elif choice == 0: ai_score += 1
                elif i == 20:  # Tech club role
                    if choice == 2: computing_score += 1
                    elif choice == 0: cybersecurity_score += 1
                    elif choice == 1: ai_score += 1

        # Learning Style & Habits (Q21–Q25)
        for i, answer in enumerate(survey_answers[10:15], 21):
            if answer:
                choice = answer[0] if isinstance(answer, list) else answer
                if i == 21:  # Learning method
                    if choice == 1: computing_score += 1
                    elif choice == 0: cybersecurity_score += 1
                    elif choice == 2: ai_score += 1
                elif i == 22:  # Study style
                    if choice == 1: ai_score += 1
                    elif choice == 0: cybersecurity_score += 1
                    elif choice == 2: computing_score += 1
                elif i == 23:  # Motivation
                    if choice == 2: computing_score += 1
                    elif choice == 1: cybersecurity_score += 1
                    elif choice == 0: ai_score += 1
                elif i == 24:  # Group role
                    if choice == 2: computing_score += 1
                    elif choice == 1: ai_score += 1
                    elif choice == 0: cybersecurity_score += 1
                elif i == 25:  # Teacher description
                    if choice == 2: computing_score += 1
                    elif choice == 1: cybersecurity_score += 1
                    elif choice == 0: ai_score += 1

        # Determine recommendation
        scores = {
            'Computing': computing_score,
            'Cybersecurity': cybersecurity_score,
            'AI': ai_score
        }
        max_score = max(scores.values())
        if list(scores.values()).count(max_score) > 1:
            # Tie-breaker: Use learning style and personality (Q16–Q25)
            tiebreaker_scores = {'Computing': 0, 'Cybersecurity': 0, 'AI': 0}
            for i, answer in enumerate(survey_answers[5:15], 16):
                if answer:
                    choice = answer[0] if isinstance(answer, list) else answer
                    if i in [16, 17, 18, 19, 20, 21, 22, 23, 24, 25]:
                        if choice in [0, 1, 2]:
                            if i == 16 and choice == 2: tiebreaker_scores['Computing'] += 1
                            elif i == 16 and choice == 1: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 16 and choice == 0: tiebreaker_scores['AI'] += 1
                            elif i == 17 and choice == 0: tiebreaker_scores['Computing'] += 1
                            elif i == 17 and choice == 2: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 17 and choice == 1: tiebreaker_scores['AI'] += 1
                            elif i == 18 and choice == 2: tiebreaker_scores['Computing'] += 1
                            elif i == 18 and choice == 1: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 18 and choice == 0: tiebreaker_scores['AI'] += 1
                            elif i == 19 and choice == 1: tiebreaker_scores['Computing'] += 1
                            elif i == 19 and choice == 2: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 19 and choice == 0: tiebreaker_scores['AI'] += 1
                            elif i == 20 and choice == 2: tiebreaker_scores['Computing'] += 1
                            elif i == 20 and choice == 0: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 20 and choice == 1: tiebreaker_scores['AI'] += 1
                            elif i == 21 and choice == 1: tiebreaker_scores['Computing'] += 1
                            elif i == 21 and choice == 0: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 21 and choice == 2: tiebreaker_scores['AI'] += 1
                            elif i == 22 and choice == 2: tiebreaker_scores['Computing'] += 1
                            elif i == 22 and choice == 0: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 22 and choice == 1: tiebreaker_scores['AI'] += 1
                            elif i == 23 and choice == 2: tiebreaker_scores['Computing'] += 1
                            elif i == 23 and choice == 1: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 23 and choice == 0: tiebreaker_scores['AI'] += 1
                            elif i == 24 and choice == 2: tiebreaker_scores['Computing'] += 1
                            elif i == 24 and choice == 1: tiebreaker_scores['AI'] += 1
                            elif i == 24 and choice == 0: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 25 and choice == 2: tiebreaker_scores['Computing'] += 1
                            elif i == 25 and choice == 1: tiebreaker_scores['Cybersecurity'] += 1
                            elif i == 25 and choice == 0: tiebreaker_scores['AI'] += 1
            recommendation = max(tiebreaker_scores, key=tiebreaker_scores.get)
        else:
            recommendation = max(scores, key=scores.get)

        return recommendation, {'AI': ai_score, 'Computing': computing_score, 'Cybersecurity': cybersecurity_score}

    try:
        for url in urls:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Debug: Log the raw response structure
            logger.debug("API Response: %s", data)

            # Process results
            results = data.get('results', [])
            if not isinstance(results, list):
                logger.error("Expected 'results' to be a list, got: %s", type(results))
                continue

            # Extract answers and coursePoints
            answers_data = next((item for item in results if item.get('key') == 'answers'), None)
            course_points_data = next((item for item in results if item.get('key') == 'coursePoints'), None)

            if answers_data and isinstance(answers_data.get('value'), list):
                player_id = answers_data.get('key')  # Using 'answers' as the player identifier
                AnswerRecord.objects.filter(player_id=player_id).delete()
                for record in answers_data['value']:
                    AnswerRecord.objects.update_or_create(
                        player_id=player_id,
                        index=record.get('index'),
                        defaults={
                            'question_id': record.get('questionID'),
                            'question_type': record.get('questionType'),
                            'selected_option_id': record.get('selectedOptionID', ''),
                            'course': record.get('course', ''),
                            'points_earned': record.get('pointsEarned', 0),
                        }
                    )

                # Extract survey and quiz answers
                answer_records = AnswerRecord.objects.filter(player_id=player_id).order_by('index')
                survey_answers = [r.selected_option_id for r in answer_records if r.question_type == 'preference' and 0 <= r.index < 15]
                quiz_answers = [r.selected_option_id for r in answer_records if r.question_type == 'knowledge']

                # Compare with correct answers for correctness
                correctness = []
                for user_answer, correct_answer in zip(quiz_answers, correct_answers):
                    user_answer = [int(a) if a.isdigit() else a for a in user_answer.split(',')] if user_answer else []
                    if compare_answers(user_answer, correct_answer):
                        correctness.append(1)
                    else:
                        correctness.append(0)

                # Calculate recommendation and scores
                recommendation, scores = recommend_course(survey_answers, quiz_answers, correctness)

                # Update SurveyResponse with coursePoints if available
                if course_points_data and isinstance(course_points_data.get('value'), dict):
                    course_points = course_points_data['value']
                    survey_response, created = SurveyResponse.objects.update_or_create(
                        player_id=player_id,
                        defaults={
                            'ai_points': course_points.get('AI', 0),
                            'computing_points': course_points.get('Computing', 0),
                            'cybersecurity_points': course_points.get('Cybersecurity', 0),
                            'recommendation': recommendation,
                        }
                    )

                key_value_pairs[player_id] = {
                    'player_id': player_id,
                    'total_score': survey_response.total_score if 'survey_response' in locals() else 0,
                    'recommendation': recommendation,
                    'ai_points': course_points.get('AI', 0),
                    'computing_points': course_points.get('Computing', 0),
                    'cybersecurity_points': course_points.get('Cybersecurity', 0),
                }

    except requests.exceptions.RequestException as e:
        logger.error("API request failed: %s", e)
    except json.JSONDecodeError as e:
        logger.error("Failed to decode JSON response: %s", e)
    except Exception as e:
        logger.error("Unexpected error in index view: %s", e)

    return render(request, 'dashboard/index.html', {'key_value_pairs': key_value_pairs})

def analytics(request):
    question_pick_rates = {f'q{i}': Counter() for i in range(1, 31)}
    recommendation_distribution = {'AI': 0, 'Computing': 0, 'Cybersecurity': 0}

    answers = AnswerRecord.objects.all()
    for answer in answers:
        question_pick_rates[f'q{answer.question_id}'][answer.selected_option_id] += 1
        if answer.question_type == 'knowledge' and answer.points_earned > 0:
            recommendation_distribution[answer.course] += answer.points_earned

    question_chart_data = {}
    for q, counter in question_pick_rates.items():
        total = sum(counter.values()) or 1
        labels = [str(k) for k in sorted(counter.keys())]
        values = [v / total * 100 for v in [counter.get(k, 0) for k in sorted(counter.keys())]]
        question_chart_data[q] = {'labels': labels, 'values': values}

    total_points = sum(recommendation_distribution.values()) or 1
    recommendation_pie_data = {
        'labels': ['AI', 'Computing', 'Cybersecurity'],
        'values': [recommendation_distribution[c] / total_points * 100 for c in ['AI', 'Computing', 'Cybersecurity']]
    }

    context = {
        'question_chart_data': question_chart_data,
        'recommendation_pie_data': recommendation_pie_data,
        'total_responses': SurveyResponse.objects.count()
    }
    return render(request, 'dashboard/analytics.html', context)

def individual(request):
    record = None
    error = None
    chart_data = {}
    quiz_responses = []

    player_id = request.GET.get('key')
    if player_id:
        try:
            answer_records = AnswerRecord.objects.filter(player_id=player_id)
            if answer_records.exists():
                record = {'player_id': player_id}
                correctness = [a.points_earned > 0 for a in answer_records if a.question_type == 'knowledge']
                chart_data = {
                    'labels': [f'Q{i}' for i in sorted(set(a.question_id for a in answer_records))],
                    'values': [100 if c else 0 for c in correctness]
                }
                for a in answer_records:
                    quiz_responses.append({
                        'question': f'Question {a.question_id}',
                        'response': a.selected_option_id,
                        'correct': 'Correct' if a.points_earned > 0 else 'Incorrect'
                    })
        except Exception as e:
            error = f"No data found for player {player_id}: {str(e)}"

    context = {'record': record, 'error': error, 'chart_data': chart_data, 'quiz_responses': quiz_responses}
    return render(request, 'dashboard/individual.html', context)

def download(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="survey_responses.csv"'
    writer = csv.writer(response)
    headers = ['player_id', 'total_score', 'ai_points', 'computing_points', 'cybersecurity_points', 'recommendation']
    headers.extend([f'Q{i}_option' for i in range(1, 31)])
    headers.extend([f'Q{i}_correct' for i in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]])
    writer.writerow(headers)

    responses = SurveyResponse.objects.all()
    for response in responses:
        row = [
            response.player_id,
            response.total_score,
            response.ai_points,
            response.computing_points,
            response.cybersecurity_points,
            response.recommendation
        ]
        answers = AnswerRecord.objects.filter(player_id=response.player_id).order_by('question_id')
        for i in range(1, 31):
            answer = answers.filter(question_id=i).first()
            row.append(answer.selected_option_id if answer else '')
        for i in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]:
            answer = answers.filter(question_id=i).first()
            row.append('Correct' if (answer and answer.points_earned > 0) else '')
        writer.writerow(row)

    return response
