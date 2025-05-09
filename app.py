import streamlit as st 
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dialer Report", page_icon=":material/analytics:", layout="wide", menu_items={})

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)


with st.sidebar:
    uploaded_file = st.file_uploader('Import Dialer Export', type='csv')

    if uploaded_file:

        try:
            file_name = uploaded_file.name.split('-Completed')[0].replace('PSE-','')
            data = pd.read_csv(uploaded_file)
            data['Campaign'] = file_name

            # Filter dialer call outcomes
            dialer_calls = data[data['Number Type.1'] == 'mobile_number']\
                        .sort_values(by='Time')\
                        .fillna('')
            
            # Filter dialer CDRS
            dialer_cdrs = data[(data['ID'].isna()) & (data['Time'] != 'ID')]
            dialer_cdrs = dialer_cdrs.drop(columns=['ID'])
            dialer_cdrs.columns = ['ID','Time','Call Duration','Ring Duration','Talk Duration','Status','Reason','Outbound Caller ID','Recording File', 'Campaign']
            dialer_cdrs['Call Duration'] = dialer_cdrs['Call Duration'].str.strip().astype(int)
            dialer_cdrs['Ring Duration'] = dialer_cdrs['Ring Duration'].str.strip().astype(int)
            dialer_cdrs['Talk Duration'] = dialer_cdrs['Talk Duration'].str.strip().astype(int)
            dialer_cdrs = dialer_cdrs.drop(columns='Recording File')
            dialer_cdrs = dialer_cdrs.fillna('').sort_values(by=['Time'])

            # Add data to session state
            st.session_state['dialer_calls'] = dialer_calls
            st.session_state['dialer_cdrs'] = dialer_cdrs

        except Exception as e:
            print(f"Error: {e}")
            st.error("Please load the 'Already Dialed' data export to proceed.")
            


if 'dialer_calls' in st.session_state:
    dialer_calls = st.session_state['dialer_calls']

    # === Row 1: Metrics === #
    total_calls = dialer_calls['ID'].count()
    abandoned_calls = dialer_calls[dialer_calls['Dial Result'] == 'R-Abandon']['ID'].count()
    failed_calls = dialer_calls[dialer_calls['Dial Result'] == 'F-Failed']['ID'].count()
    complete_calls = dialer_calls[dialer_calls['Dial Result'] == 'C-Completed']['ID'].count()
    no_answer = dialer_calls[dialer_calls['Dial Result'] == 'R-No Answer']['ID'].count()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric('Total Calls', total_calls)
    with col2:
        st.metric('Complete Calls', complete_calls)
    with col3:
        st.metric('Failed', failed_calls)
    with col4:
        st.metric('Abandoned Calls', abandoned_calls)
    with col5:
        st.metric('No Answer', no_answer)

    # === Row 2: Charts === #
    col1, col2, col3 = st.columns(3)

    with col1:
        # Group by Agent ANswered Calls
        answered_calls_counts = dialer_calls['Agent'].value_counts(dropna=False).reset_index()
        answered_calls_counts.columns = ['Agent', 'Count']
        fig = px.bar(answered_calls_counts, x="Agent", y="Count", title='Agent Answered Calls')
        st.plotly_chart(fig)

    with col2:
        # Group by 'Call Disposition' and count occurrences
        dispo_counts = dialer_calls['Call Disposition'].value_counts(dropna=False).reset_index()
        dispo_counts.columns = ['Call Disposition', 'Count']
        fig = px.pie(dispo_counts, values='Count', names='Call Disposition', title='Call Dispositions')
        st.plotly_chart(fig)

    with col3:
        # Group by 'Dial Result' and count occurrences
        dial_result_counts = dialer_calls['Dial Result'].value_counts(dropna=False).reset_index()
        dial_result_counts.columns = ['Dial Result', 'Count']
        fig = px.bar(dial_result_counts, x='Dial Result', y='Count', title='Dial Outcomes')
        st.plotly_chart(fig)


    # === Row 3: Dialer Call records === #

    with st.container():
        st.header('Dialer Call Results')
        st.dataframe(dialer_calls, use_container_width=True, hide_index=True)

    # === Row 4: Dialer CDRS === #
    # if 'dialer_cdrs' in st.session_state:
    #     dialer_cdrs = st.session_state['dialer_cdrs']
    #     with st.container():
    #         st.header('Dialer CDRS')
    #         st.dataframe(dialer_cdrs, use_container_width=True, hide_index=True)