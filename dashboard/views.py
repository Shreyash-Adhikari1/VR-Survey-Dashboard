import io
import json
from collections import Counter
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
import requests
import csv
from .models import SurveyResponse
import logging



# Configure logging
logger = logging.getLogger(__name__)

def index(request):
    # API endpoints (replace with your actual API endpoint)
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

    key_value_pairs = {}  # For passing to the template

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
        computing_questions = [6, 9, 13, 14]  # Q6, Q9, Q13, Q14
        cybersecurity_questions = [7, 11, 27, 30]  # Q7, Q11, Q27, Q30
        ai_questions = [8, 10, 12, 15, 26, 28, 29]  # Q8, Q10, Q12, Q15, Q26, Q28, Q29

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
                    if choice == 1: ai_score += 1
                    elif choice == 0: cybersecurity_score += 1
                    elif choice == 2: computing_score += 1

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
                        if choice in [0, 1, 2]:  # Adjust based on question
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
            max_tiebreaker = max(tiebreaker_scores.values())
            recommendation = max(tiebreaker_scores, key=tiebreaker_scores.get)
        else:
            recommendation = max(scores, key=scores.get)

        return recommendation, scores

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

            for item in results:
                if not isinstance(item, dict):
                    logger.error("Expected item to be a dict, got: %s (%s)", item, type(item))
                    continue
                key = item.get('key')
                if key is None:
                    logger.error("Item missing 'key': %s", item)
                    continue

                value = item.get('value', {})
                if not isinstance(value, dict):
                    logger.error("Expected 'value' to be a dict, got: %s (%s)", value, type(value))
                    continue

                answers = value.get('answers', [])
                score = value.get('score', 0)

                survey_answers = answers[:15] if len(answers) >= 15 else answers
                quiz_answers = answers[15:] if len(answers) > 15 else []

                correctness = []
                for user_answer, correct_answer in zip(quiz_answers, correct_answers):
                    if compare_answers(user_answer, correct_answer):
                        correctness.append(1)
                    else:
                        correctness.append(0)

                correct_sum = sum(correctness)
                skipped = correct_sum != score

                survey_answers_str = json.dumps(survey_answers)
                quiz_answers_str = json.dumps(quiz_answers)
                correctness_str = ','.join(map(str, correctness))
                recommendation, scores = recommend_course(survey_answers, quiz_answers, correctness)

                # Update or create the model instance
                SurveyResponse.objects.update_or_create(
                    id=key,
                    defaults={
                        'selected_options_from_one_to_five': survey_answers_str,
                        'selected_options_rest_questions': quiz_answers_str,
                        'score': score,
                        'correctly_answered': correctness_str,
                        'skipped': skipped,
                        'recommendation': recommendation,
                        'computing_score': scores['Computing'],
                        'cybersecurity_score': scores['Cybersecurity'],
                        'ai_score': scores['AI'],
                    }
                )

        # Fetch all survey responses
        responses = SurveyResponse.objects.all()
        for response in responses:
            gender_display = response.get_gender_display() if response.gender else ''
            key_value_pairs[response.id] = {
                'name': response.name or '',
                'gender': gender_display,
                'score': response.score,
                'skipped': 'Yes' if response.skipped else 'No',
                'recommendation': response.recommendation,
                'computing_score': response.computing_score,
                'cybersecurity_score': response.cybersecurity_score,
                'ai_score': response.ai_score,
            }

    except requests.exceptions.RequestException as e:
        logger.error("API request failed: %s", e)
    except json.JSONDecodeError as e:
        logger.error("Failed to decode JSON response: %s", e)
    except Exception as e:
        logger.error("Unexpected error in index view: %s", e)

    return render(request, 'dashboard/index.html', {'key_value_pairs': key_value_pairs})


def analytics(request):
    # Initialize data structures
    survey_data = {f'q{i}': Counter() for i in range(1, 26)}  # Q1–Q25
    quiz_data = {f'q{i}': Counter() for i in range(26, 31)}  # Q26–Q30
    correctness_data = {f'q{i}': {'correct': 0, 'total': 0} for i in range(6, 16)}  # Q6–Q15
    correctness_data.update({f'q{i}': {'correct': 0, 'total': 0} for i in range(26, 31)})  # Q26–Q30
    skipped_correctness = {
        f'q{i}': {'skipped': {'correct': 0, 'total': 0}, 'not_skipped': {'correct': 0, 'total': 0}}
        for i in range(6, 16)
    }
    skipped_correctness.update({
        f'q{i}': {'skipped': {'correct': 0, 'total': 0}, 'not_skipped': {'correct': 0, 'total': 0}}
        for i in range(26, 31)
    })
    skipped_distribution = {'skipped': 0, 'not_skipped': 0}
    recommendation_distribution = {'Computing': 0, 'Cybersecurity': 0, 'AI': 0}

    # Option mappings for survey questions
    survey_options = {
        'q1': {0: 'Software Developer', 1: 'Cybersecurity Analyst', 2: 'AI Engineer'},
        'q2': {0: 'Finding bugs', 1: 'Designing algorithms', 2: 'Building applications'},
        'q3': {0: 'Problem solver', 1: 'Security checker', 2: 'Innovator'},
        'q4': {0: 'Machine thinking', 1: 'Preventing threats', 2: 'Creating tools'},
        'q5': {0: 'Data privacy', 1: 'Neural networks', 2: 'Software engineering'},
        'q16': {0: 'Alone', 1: 'In a team', 2: 'Creative environment'},
        'q17': {0: 'Googling', 1: 'Root cause', 2: 'Reporting'},
        'q18': {0: 'Curious', 1: 'Strategic', 2: 'Hands-on'},
        'q19': {0: 'Books', 1: 'Tutorials', 2: 'Lectures'},
        'q20': {0: 'Hacking systems', 1: 'ML projects', 2: 'Apps/websites'},
        'q21': {0: 'Watching videos', 1: 'Trying yourself', 2: 'Reading articles'},
        'q22': {0: 'Talking', 1: 'Writing', 2: 'Visualizing'},
        'q23': {0: 'Solving puzzles', 1: 'Competing', 2: 'Creating features'},
        'q24': {0: 'Take the lead', 1: 'Analyze ideas', 2: 'Do practicals'},
        'q25': {0: 'Analytical', 1: 'Quick', 2: 'Diligent'},
    }

    # Option mappings for quiz questions
    quiz_options = {
        'q6': {0: 'Hyper Trainer', 1: 'Hyper Text', 2: 'Home Tool'},
        'q7': {0: 'password123', 1: 'HelloWorld', 2: 'X$9!q@T#nP'},
        'q8': {0: 'True', 1: 'False', 2: 'Error'},
        'q9': {0: 'If-else', 1: 'While', 2: 'Array'},
        'q10': {0: '20', 1: '32', 2: '18'},
        'q11': {0: 'Fishing', 1: 'Social engineering', 2: 'Device cloning'},
        'q12': {0: 'Artificial Interface', 1: 'Automatic Intelligence', 2: 'Artificial Intelligence'},
        'q13': {0: 'Python', 1: 'Java', 2: 'Excel'},
        'q14': {0: 'Repeating actions', 1: 'Storing data', 2: 'Testing variables'},
        'q15': {0: 'True', 1: 'False', 2: 'Error'},
        'q26': {0: 'Creating viruses', 1: 'Teaching computers', 2: 'Installing OS'},
        'q27': {0: 'Backup', 1: 'Data transfer', 2: 'Network protection'},
        'q28': {0: '20', 1: '14', 2: '24'},
        'q29': {0: 'Rules', 1: 'Data', 2: 'Design'},
        'q30': {0: 'Cybersecurity', 1: 'Project Manager', 2: 'AI Ethics'},
    }

    responses = SurveyResponse.objects.all()
    total_responses = responses.count()

    for response in responses:
        try:
            # Parse survey answers (Q1–Q25)
            survey_answers = json.loads(response.selected_options_from_one_to_five or '[]')
            for i, answer in enumerate(survey_answers[:25], 1):
                if answer:
                    survey_data[f'q{i}'][answer[0]] += 1

            # Parse quiz answers and correctness (Q6–Q15, Q26–Q30)
            quiz_answers = json.loads(response.selected_options_rest_questions or '[]')
            correctness = [int(x) for x in (response.correctly_answered or '').split(',') if x]
            quiz_indices = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]
            for i, (answer, correct) in zip(quiz_indices, zip(quiz_answers, correctness)):
                if answer:
                    quiz_data[f'q{i}'][answer[0]] += 1
                correctness_data[f'q{i}']['total'] += 1
                correctness_data[f'q{i}']['correct'] += correct
                skip_key = 'skipped' if response.skipped else 'not_skipped'
                skipped_correctness[f'q{i}'][skip_key]['total'] += 1
                skipped_correctness[f'q{i}'][skip_key]['correct'] += correct

            # Track skipped and recommendation distribution
            skipped_distribution['skipped' if response.skipped else 'not_skipped'] += 1
            recommendation_distribution[response.recommendation] += 1

        except json.JSONDecodeError:
            continue

    # Prepare chart data
    survey_chart_data = {}
    for q, counter in survey_data.items():
        labels = [survey_options[q].get(k, str(k)) for k in sorted(counter.keys())]
        values = [counter.get(k, 0) / max(total_responses, 1) * 100 for k in sorted(counter.keys())]
        survey_chart_data[q] = {
            'labels': labels,
            'values': values,
            'type': 'bar',
            'scales': json.dumps({'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Percentage (%)'}}}),
            'legend_display': False
        }

    quiz_chart_data = {}
    for q, counter in quiz_data.items():
        labels = [quiz_options[q].get(k, str(k)) for k in sorted(counter.keys())]
        values = [counter.get(k, 0) / max(total_responses, 1) * 100 for k in sorted(counter.keys())]
        quiz_chart_data[q] = {'labels': labels, 'values': values}

    correctness_chart_data = {
        'labels': [f'Q{i}' for i in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]],
        'values': [
            (data['correct'] / max(data['total'], 1) * 100) if data['total'] > 0 else 0
            for data in correctness_data.values()
        ]
    }

    skipped_correctness_chart_data = {
        'labels': [f'Q{i}' for i in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]],
        'skipped': [
            (data['skipped']['correct'] / max(data['skipped']['total'], 1) * 100) if data['skipped']['total'] > 0 else 0
            for data in skipped_correctness.values()
        ],
        'not_skipped': [
            (data['not_skipped']['correct'] / max(data['not_skipped']['total'], 1) * 100) if data['not_skipped']['total'] > 0 else 0
            for data in skipped_correctness.values()
        ]
    }

    recommendation_pie_data = {
        'labels': ['Computing', 'Cybersecurity', 'AI'],
        'values': [
            recommendation_distribution['Computing'] / max(total_responses, 1) * 100,
            recommendation_distribution['Cybersecurity'] / max(total_responses, 1) * 100,
            recommendation_distribution['AI'] / max(total_responses, 1) * 100
        ]
    }

    context = {
        'survey_chart_data': survey_chart_data,
        'quiz_chart_data': quiz_chart_data,
        'correctness_chart_data': correctness_chart_data,
        'skipped_correctness_chart_data': skipped_correctness_chart_data,
        'recommendation_pie_data': recommendation_pie_data,
        'total_responses': total_responses
    }

    return render(request, 'dashboard/analytics.html', context)

def individual(request):
    record = None
    error = None
    chart_data = {}
    quiz_responses = []

    # Search functionality
    key = request.GET.get('key')
    if key:
        try:
            record = SurveyResponse.objects.get(id=key)
        except SurveyResponse.DoesNotExist:
            error = "No student found with this ID."

    if record:
        # Quiz options mapping
        quiz_options = {
            'q6': {0: 'Hyper Trainer', 1: 'Hyper Text', 2: 'Home Tool'},
            'q7': {0: 'password123', 1: 'HelloWorld', 2: 'X$9!q@T#nP'},
            'q8': {0: 'True', 1: 'False', 2: 'Error'},
            'q9': {0: 'If-else', 1: 'While', 2: 'Array'},
            'q10': {0: '20', 1: '32', 2: '18'},
            'q11': {0: 'Fishing', 1: 'Social engineering', 2: 'Device cloning'},
            'q12': {0: 'Artificial Interface', 1: 'Automatic Intelligence', 2: 'Artificial Intelligence'},
            'q13': {0: 'Python', 1: 'Java', 2: 'Excel'},
            'q14': {0: 'Repeating actions', 1: 'Storing data', 2: 'Testing variables'},
            'q15': {0: 'True', 1: 'False', 2: 'Error'},
            'q26': {0: 'Creating viruses', 1: 'Teaching computers', 2: 'Installing OS'},
            'q27': {0: 'Backup', 1: 'Data transfer', 2: 'Network protection'},
            'q28': {0: '20', 1: '14', 2: '24'},
            'q29': {0: 'Rules', 1: 'Data', 2: 'Design'},
            'q30': {0: 'Cybersecurity', 1: 'Project Manager', 2: 'AI Ethics'},
        }

        # Parse quiz answers and correctness
        quiz_answers = json.loads(record.selected_options_rest_questions or '[]')
        correctness = [int(x) for x in (record.correctly_answered or '').split(',') if x]

        # Line chart data for correctness
        chart_data = {
            'labels': [f'Q{i}' for i in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]],
            'values': [100 if correct else 0 for correct in correctness]
        }

        # Quiz responses for table
        quiz_indices = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]
        for i, (answer, correct) in zip(quiz_indices, zip(quiz_answers, correctness)):
            q = f'q{i}'
            if answer:
                response_text = quiz_options[q].get(answer[0], str(answer[0]))
                quiz_responses.append({
                    'question': f'Question {i}',
                    'response': response_text,
                    'correct': 'Correct' if correct else 'Incorrect'
                })

    context = {
        'record': record,
        'error': error,
        'chart_data': chart_data,
        'quiz_responses': quiz_responses
    }
    return render(request, 'dashboard/individual.html', context)

def download(request):
    # Define response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="survey_responses.csv"'

    # Option mappings
    survey_options = {
        'q1': {0: 'Software Developer', 1: 'Cybersecurity Analyst', 2: 'AI Engineer'},
        'q2': {0: 'Finding bugs', 1: 'Designing algorithms', 2: 'Building applications'},
        'q3': {0: 'Problem solver', 1: 'Security checker', 2: 'Innovator'},
        'q4': {0: 'Machine thinking', 1: 'Preventing threats', 2: 'Creating tools'},
        'q5': {0: 'Data privacy', 1: 'Neural networks', 2: 'Software engineering'},
        'q16': {0: 'Alone', 1: 'In a team', 2: 'Creative environment'},
        'q17': {0: 'Googling', 1: 'Root cause', 2: 'Reporting'},
        'q18': {0: 'Curious', 1: 'Strategic', 2: 'Hands-on'},
        'q19': {0: 'Books', 1: 'Tutorials', 2: 'Lectures'},
        'q20': {0: 'Hacking systems', 1: 'ML projects', 2: 'Apps/websites'},
        'q21': {0: 'Watching videos', 1: 'Trying yourself', 2: 'Reading articles'},
        'q22': {0: 'Talking', 1: 'Writing', 2: 'Visualizing'},
        'q23': {0: 'Solving puzzles', 1: 'Competing', 2: 'Creating features'},
        'q24': {0: 'Take the lead', 1: 'Analyze ideas', 2: 'Do practicals'},
        'q25': {0: 'Analytical', 1: 'Quick', 2: 'Diligent'},
    }

    quiz_options = {
        'q6': {0: 'Hyper Trainer', 1: 'Hyper Text', 2: 'Home Tool'},
        'q7': {0: 'password123', 1: 'HelloWorld', 2: 'X$9!q@T#nP'},
        'q8': {0: 'True', 1: 'False', 2: 'Error'},
        'q9': {0: 'If-else', 1: 'While', 2: 'Array'},
        'q10': {0: '20', 1: '32', 2: '18'},
        'q11': {0: 'Fishing', 1: 'Social engineering', 2: 'Device cloning'},
        'q12': {0: 'Artificial Interface', 1: 'Automatic Intelligence', 2: 'Artificial Intelligence'},
        'q13': {0: 'Python', 1: 'Java', 2: 'Excel'},
        'q14': {0: 'Repeating actions', 1: 'Storing data', 2: 'Testing variables'},
        'q15': {0: 'True', 1: 'False', 2: 'Error'},
        'q26': {0: 'Creating viruses', 1: 'Teaching computers', 2: 'Installing OS'},
        'q27': {0: 'Backup', 1: 'Data transfer', 2: 'Network protection'},
        'q28': {0: '20', 1: '14', 2: '24'},
        'q29': {0: 'Rules', 1: 'Data', 2: 'Design'},
        'q30': {0: 'Cybersecurity', 1: 'Project Manager', 2: 'AI Ethics'},
    }

    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header
    headers = ['id', 'name', 'gender', 'score', 'skipped', 'recommendation', 'computing_score', 'cybersecurity_score', 'ai_score']
    headers.extend([f'Q{i}' for i in range(1, 31)])
    headers.extend([f'Q{i}_correct' for i in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]])
    writer.writerow(headers)

    # Fetch all responses
    responses = SurveyResponse.objects.all()

    for record in responses:
        row = [
            record.id,
            record.name or '',
            record.get_gender_display() if record.gender else '',
            record.score,
            'Yes' if record.skipped else 'No',
            record.recommendation,
            record.computing_score,
            record.cybersecurity_score,
            record.ai_score
        ]

        # Parse survey answers (Q1–Q25)
        survey_answers = json.loads(record.selected_options_from_one_to_five or '[]')
        for i in range(1, 26):
            q = f'q{i}'
            if i-1 < len(survey_answers) and survey_answers[i-1]:
                answer = survey_options[q].get(survey_answers[i-1][0], str(survey_answers[i-1][0]))
            else:
                answer = ''
            row.append(answer)

        # Parse quiz answers (Q6–Q15, Q26–Q30)
        quiz_answers = json.loads(record.selected_options_rest_questions or '[]')
        quiz_indices = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]
        quiz_answer_dict = {i: quiz_answers[i-6] if i-6 < len(quiz_answers) else [] for i in quiz_indices}
        for i in range(6, 31):
            q = f'q{i}'
            answer = ''
            if i in quiz_answer_dict and quiz_answer_dict[i]:
                answer = quiz_options[q].get(quiz_answer_dict[i][0], str(quiz_answer_dict[i][0]))
            row.append(answer)

        # Parse correctness
        correctness = [int(x) for x in (record.correctly_answered or '').split(',') if x]
        for i in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 30]:
            if i-6 < len(correctness):
                correct = 'Correct' if correctness[i-6] else 'Incorrect'
            else:
                correct = ''
            row.append(correct)

        writer.writerow(row)

    return response
