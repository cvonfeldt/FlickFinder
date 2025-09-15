from django.shortcuts import render
from .models import User
from .forms import UserPreferenceForm

import openai
import requests
import json
import re
import os

openai.api_key = os.getenv('OPEN_API_KEY')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

import re

def clean_response(response_data, filetype=''):
    """
    Extract and clean content based on the filetype.
    For 'json', extract JSON content enclosed within ```json and ```.
    For other filetypes or plain text, handle accordingly.
    """
    if filetype == 'json':
        # Regex to match content between ```json and ```
        regex = r"```json\n(.*?)```"
        match = re.search(regex, response_data, re.DOTALL)
        
        if match:
            # Extract and return the cleaned JSON content
            json_content = match.group(1).strip()
            return json_content
        
    elif filetype == '':
        # Regex to remove code blocks (``` and ```), can handle plain text
        cleaned_data = re.sub(r"```.*?```", "", response_data, flags=re.DOTALL).strip()
        return cleaned_data
    
    else:
        return response_data.strip()

    # If no match is found, return the original response or raise an error
    return response_data.strip()

def get_movie_poster_url(title):
    # Query OMDB API for movie details, including poster URL
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    movie_data = response.json()
    
    if movie_data.get("Response") == "True":
        return movie_data.get("Poster", "")  # Return the poster URL
    else:
        return ""

def get_movie_recommendations(user_input):
    # Requesting GPT to provide detailed information for movie recommendations
    response = openai.chat.completions.create(
        model="gpt-4o-2024-11-20",  # You can use GPT-4 or another model if preferred
        messages=[
            {"role": "system", "content": "You are a helpful assistant that suggests movies based on user preferences."},
            {"role": "user", "content": f"""Based on the following preferences: {user_input}, recommend 15 movies. For each movie, 
                    provide a JSON object with the following fields: 'title', 'release_year', 'description', 'score' (relevance score from 1-10), 
                    and 'explanation' (a brief reason why the movie is recommended, written in the tone of a Gen-Z boy). 
                    Return all movie recommendations as a list of JSON objects."""}
        ]
    )

    # Parsing the result and returning the movie details
    movie_data = response.choices[0].message.content.strip()
    cleaned_data = clean_response(movie_data, filetype='json')

    try:
        rec_dic = json.loads(cleaned_data)
        for movie in rec_dic:
            title = movie.get('title')
            movie["poster"] = get_movie_poster_url(title)
        return rec_dic
    except json.JSONDecodeError:

        print(f"Error parsing response: {cleaned_data}")
        return []

def combine_preferences_with_api(old_preferences, new_preferences):
    prompt = f"""
    The following are two sets of movie preferences from the same user. Please combine them into a single, cohesive set of preferences. 
    Your task is to merge the preferences while maintaining the user's tone, language, and intent. The result should sound like something the user would say, 
    and it should keep the same level of detail, style, and character that is present in the original preferences.

    Old Preferences: 
    {old_preferences}

    New Preferences:
    {new_preferences}

    Return a single coherent preference that incorporates both sets of preferences in a way that reflects the user's unique voice and interests.
    """

    # Requesting GPT to combine the preferences while maintaining the user's tone
    response = openai.chat.completions.create(
        model="gpt-4o-2024-11-20",  # You can use GPT-4 or another model
        messages=[
            {"role": "system", "content": "You are an assistant that combines movie preferences while preserving the user's tone and style."},
            {"role": "user", "content": prompt}
        ]
    )

    # Get the combined preferences from GPT and strip any extra whitespace
    combined_preferences = response.choices[0].message.content.strip()
    return clean_response(combined_preferences)



def movie_recommendations(request):
    recommendations = []
    if request.method == 'POST':
        form = UserPreferenceForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data.get('user_id')
            user_input = form.cleaned_data['preferences']
            try:
                user = User.objects.get(user_id=user_id) 
                old_preferences = user.preferences
                combined_preferences = combine_preferences_with_api(old_preferences, user_input)
                print(combined_preferences)
                recommendations = get_movie_recommendations(combined_preferences)

                user.preferences = combined_preferences
                user.save()

            except User.DoesNotExist:
                user = User.objects.create(user_id=user_id, preferences=user_input)
                recommendations = get_movie_recommendations(user_input)
    else:
        form = UserPreferenceForm()

    return render(request, 'form.html', {'form': form, 'recommendations': recommendations})
