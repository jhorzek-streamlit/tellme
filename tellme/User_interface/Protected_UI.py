"""Simpified UI using streamlit secrets for API keys and password."""

import streamlit as st
from chatlas import ChatOpenAI

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

password = st.text_input('Password', type='password')
if password:
    if password == st.secrets['auth']['password']:
        st.success('Access granted')
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
                min_value=1,
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

            chat_provider = 'OpenAI'

            ai_settings = AISettings()

            ai_settings.model_name = 'gpt-4.1'
            ai_settings.speech_model = 'gpt-4o-mini-tts'
            language = st.text_input(
                'Which language should the podcast be in?', value='English'
            )
            ai_settings.summary_instructions = SummaryInstructions(language=language)
            api_key = st.secrets['auth']['OpenAI']

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

    else:
        st.error('Incorrect password')
        st.stop()
else:
    st.warning('Please enter the password')
    st.stop()
