import requests
import json
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.conf import settings

def fetch_unity_cloud_save_data(player_id=None):
    """
    Fetch survey data from Unity Cloud Save using REST API (placeholder for now).
    """
    # Mock data until Unity integration is complete
    if player_id:
        return [
            {
                'key': 'survey_responses',
                'value': json.dumps({
                    'answers': {'q1': 4, 'q2': 3, 'q3': 5, 'q4': 2},
                    'recommended_department': 'Computing'
                }),
                'playerId': player_id
            }
        ]
    else:
        return [
            {
                'player_id': 'student123',
                'data': [
                    {
                        'key': 'survey_responses',
                        'value': json.dumps({
                            'answers': {'q1': 4, 'q2': 3, 'q3': 5, 'q4': 2},
                            'recommended_department': 'Computing'
                        })
                    }
                ]
            },
            {
                'player_id': 'student456',
                'data': [
                    {
                        'key': 'survey_responses',
                        'value': json.dumps({
                            'answers': {'q1': 3, 'q2': 4, 'q3': 4, 'q4': 3},
                            'recommended_department': 'Ethical Hacking'
                        })
                    }
                ]
            },
            {
                'player_id': 'student789',
                'data': [
                    {
                        'key': 'survey_responses',
                        'value': json.dumps({
                            'answers': {'q1': 5, 'q2': 5, 'q3': 4, 'q4': 4},
                            'recommended_department': 'Computing with AI'
                        })
                    }
                ]
            }
        ]

def process_survey_data(data):
    """
    Process survey data retrieved from Unity Cloud Save.
    """
    if not data:
        return None
    
    processed = []
    for item in data:
        if item.get("key") == "survey_responses":
            responses = json.loads(item.get("value", "{}"))
            processed.append({
                "player_id": item.get("playerId"),
                "responses": responses.get("answers", {}),
                "recommendation": responses.get("recommended_department")
            })
    return processed

def generic_dashboard(request):
    """
    Render the generic dashboard with average survey answers and field suitability.
    """
    raw_data = fetch_unity_cloud_save_data()
    if not raw_data:
        return HttpResponseBadRequest("Failed to fetch data from Unity Cloud Save.")
    
    processed_data = []
    for player_data in raw_data:
        processed = process_survey_data(player_data['data'])
        if processed:
            processed_data.extend(processed)
    
    if not processed_data:
        return render(request, 'dashboard/generic_dashboard.html', {'error': 'No survey data available.'})
    
    # Calculate averages
    question_sums = {}
    question_counts = {}
    for entry in processed_data:
        for qid, score in entry['responses'].items():
            question_sums[qid] = question_sums.get(qid, 0) + score
            question_counts[qid] = question_counts.get(qid, 0) + 1
    
    averages = {qid: question_sums[qid] / question_counts[qid] for qid in question_sums} if question_counts else {}
    
    # Calculate field suitability
    field_counts = {'Computing': 0, 'Ethical Hacking': 0, 'Computing with AI': 0}
    for entry in processed_data:
        rec = entry['recommendation']
        if rec in field_counts:
            field_counts[rec] += 1
    
    context = {
        'averages': averages,
        'total_responses': len(processed_data),
        'field_counts': field_counts
    }
    return render(request, 'dashboard/generic_dashboard.html', context)

def individual_dashboard(request):
    """
    Render the individual dashboard for a specific student.
    """
    player_id = request.GET.get('player_id', 'student123')
    raw_data = fetch_unity_cloud_save_data(player_id)
    if not raw_data:
        return HttpResponseBadRequest("Failed to fetch data for player.")
    
    processed_data = process_survey_data(raw_data)
    if not processed_data:
        return render(request, 'dashboard/individual_dashboard.html', {'error': 'No survey data available for this player.'})
    
    survey = processed_data[0]
    context = {
        'player_id': player_id,
        'responses': survey['responses'],
        'recommendation': survey['recommendation']
    }
    return render(request, 'dashboard/individual_dashboard.html', context)