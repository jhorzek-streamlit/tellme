"""Streamlit UI."""

import streamlit as st
from chatlas import ChatGoogle, ChatOpenAI

from tellme.AI_Podcast.podcast_setups import SofiaMark
from tellme.Settings.AI_settings import (
    AISettings,
    PodcastInstructions,
    SummaryInstructions,
)
from tellme.User_interface.attraction_map import fetch_and_create_attraction_map
from tellme.User_interface.user_location import (
    address_to_coordinates,
    get_user_location,
)

# Make sure that the following elements are kept when the app is rerun:
if 'podcasts' not in st.session_state:
    st.session_state.podcasts = {}

if 'summary' not in st.session_state:
    st.session_state.summary = {}
if 'use_gps_location' not in st.session_state:
    st.session_state.use_gps_location = True

if st.session_state.use_gps_location:
    location = get_user_location(component_key='Initial_Location')
    st.session_state.location = location

with st.sidebar:
    st.header('Location:')
    address = st.text_input(label='Address', value=None)
    if st.button('Search address'):
        location = address_to_coordinates(address=address)
        if location is None:
            st.error('Could not find the address you provided.')
        else:
            st.session_state.use_gps_location = False
            st.session_state.location = location

    if st.button('Use gps location'):
        st.session_state.use_gps_location = True

    latitude = st.session_state.location.get('latitude')
    longitude = st.session_state.location.get('longitude')
    radius = st.number_input(
        label='Enter the radius (in meters) in which you want to search for attractions:',
        min_value=15,
        max_value=10000,
        value=1000,
    )

    st.header('Wikipedia settings:')
    local = st.text_input(
        (
            'In which language should tellme search for wikipedia articles (e.g., en = English, de = German)?'
            + ' This has no influence on the language of the summaries or podcasts, but can change how many articles are found.'
            + ' Language setting for the podcast can be found in the model settings when selecting OpenAI.'
        ),
        value='de',
    )
    st.header('Model Settings')

    chat_provider = st.selectbox(
        'Choose a chat provider', ['OpenAI', 'Gemini'], index=0
    )

    ai_settings = AISettings()

    if chat_provider == 'Gemini':
        ai_settings.model_name = st.text_input(
            'Name of the AI model to use', value='gemini-2.0-flash'
        )
        ai_settings.speech_model = 'edge-tts'
        language = 'English'
        api_key = st.text_input(
            f'Your API Key for {chat_provider}',
            type='password',
            help=f'To use {chat_provider}, you need an API key. Google provides a free key that can be used for a small number of requests. Go to https://aistudio.google.com/apikey and create a new API key. Save this API key and supply it to the app to create a podcast.',
        )
    elif chat_provider == 'OpenAI':
        ai_settings.model_name = st.text_input(
            'Name of the AI model to use', value='gpt-4.1'
        )
        st.text('OpenAI will also be used to generate the voices.')
        ai_settings.speech_model = 'gpt-4o-mini-tts'
        language = st.text_input(
            'Which language should the podcast be in?', value='English'
        )
        api_key = st.text_input(
            f'Your API Key for {chat_provider}',
            type='password',
            help=f'To use {chat_provider}, you need an API key. OpenAI requires to set up a payed API key. Go to https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key and create a new API key. Save this API key and supply it to the app to create a podcast.',
        )
    ai_settings.summary_instructions = SummaryInstructions(language=language)

    match chat_provider:
        case 'Gemini':
            ai_settings.Chat = ChatGoogle
            ai_settings.podcast_instructions = PodcastInstructions(
                SofiaMark(
                    voices={'Mark': 'en-US-RogerNeural', 'Sofia': 'en-GB-SoniaNeural'},
                    language=language,
                )
            )
        case 'OpenAI':
            ai_settings.Chat = ChatOpenAI
            ai_settings.podcast_instructions = PodcastInstructions(
                SofiaMark(voices={'Mark': 'ash', 'Sofia': 'alloy'}, language=language)
            )


if (latitude is not None) and (longitude is not None) and (radius is not None):
    fetch_and_create_attraction_map(
        local=local,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        chat_provider=chat_provider,
        ai_settings=ai_settings,
        api_key=api_key,
    )
